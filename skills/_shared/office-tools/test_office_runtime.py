import io
import builtins
import tempfile
import subprocess
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import xsd_validator
import setup_schemas
import office_readiness
import validate


class SchemaValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.schemas = self.root / "schemas"
        (self.schemas / "ooxml").mkdir(parents=True)
        self.schema = self.schemas / "ooxml/wml.xsd"
        self.schema.write_text(
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">'
            '<xs:element name="document" type="xs:string"/></xs:schema>'
        )
        self.unpacked = self.root / "unpacked"
        (self.unpacked / "word").mkdir(parents=True)
        self.document = self.unpacked / "word/document.xml"
        self.document.write_text("<document>valid</document>")
        self.original = self.root / "original.docx"
        self.save_original()
        self.schema_patch = patch.object(xsd_validator, "_get_schemas_dir", return_value=self.schemas)
        self.schema_patch.start()
        self.addCleanup(self.schema_patch.stop)

    def save_original(self):
        with zipfile.ZipFile(self.original, "w") as archive:
            archive.write(self.document, "word/document.xml")

    def test_schema_compile_failure_never_passes(self):
        self.schema.write_text(
            '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" '
            'xmlns:dc="http://purl.org/dc/terms/">'
            '<xs:element ref="dc:created"/></xs:schema>'
        )
        for original in (None, self.original):
            with self.subTest(original=original):
                passed, errors = xsd_validator.validate_xsd(self.unpacked, original)
                self.assertFalse(passed)
                self.assertIn("unavailable", errors[0])

    def test_missing_schema_fails(self):
        self.schema.unlink()
        passed, errors = xsd_validator.validate_xsd(self.unpacked, self.original)
        self.assertFalse(passed)
        self.assertIn("Cannot load schema", errors[0])

    def test_missing_dependencies_fail(self):
        with patch.object(xsd_validator, "HAS_LXML", False):
            self.assertFalse(xsd_validator.validate_xsd(self.unpacked)[0])
        with patch.object(xsd_validator, "_get_schemas_dir", return_value=None):
            self.assertFalse(xsd_validator.validate_xsd(self.unpacked)[0])

    def test_unavailable_validator_module_fails(self):
        original_import = builtins.__import__

        def unavailable_import(name, *arguments, **keywords):
            if name == "xsd_validator":
                raise ImportError("missing validator")
            return original_import(name, *arguments, **keywords)

        with patch("builtins.__import__", side_effect=unavailable_import):
            result = validate.validate(self.unpacked, file_type="docx")
        self.assertIn("XSD validation unavailable: missing validator", result.errors)

    def test_valid_document_passes(self):
        self.assertEqual(xsd_validator.validate_xsd(self.unpacked), (True, []))

    def test_new_document_error_fails(self):
        self.document.write_text("<invalid/>")
        self.assertFalse(xsd_validator.validate_xsd(self.unpacked, self.original)[0])

    def test_existing_document_error_remains_accepted(self):
        self.document.write_text("<invalid/>")
        self.save_original()
        self.assertEqual(xsd_validator.validate_xsd(self.unpacked, self.original), (True, []))


class BundledSchemaTests(unittest.TestCase):
    schemas = Path(__file__).parent / "schemas"

    def test_all_roots_compile_offline(self):
        self.assertEqual(xsd_validator.check_schemas(self.schemas), [])

    def test_generated_docx_and_invalid_word_element(self):
        from docx import Document

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original = root / "original.docx"
            document = Document()
            document.add_paragraph("Schema regression")
            word_namespace = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            document.settings.element.find(f"{{{word_namespace}}}zoom").set(
                f"{{{word_namespace}}}percent", "100"
            )
            document.save(original)
            unpacked = root / "unpacked"
            with zipfile.ZipFile(original) as archive:
                archive.extractall(unpacked)
            self.assertEqual(xsd_validator.validate_xsd(unpacked), (True, []))
            document_path = unpacked / "word/document.xml"
            tree = xsd_validator.etree.parse(str(document_path))
            xsd_validator.etree.SubElement(
                tree.getroot(),
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}invalid",
            )
            tree.write(str(document_path))
            self.assertFalse(xsd_validator.validate_xsd(unpacked, original)[0])

    def test_setup_localizes_downloaded_imports(self):
        def nested_archive(folder, inner_name):
            inner_bytes = io.BytesIO()
            with zipfile.ZipFile(inner_bytes, "w") as archive:
                for schema in folder.glob("*.xsd"):
                    if schema.name in {"xml.xsd", "dc.xsd", "dcterms.xsd", "dcmitype.xsd"}:
                        continue
                    tree = xsd_validator.etree.parse(str(schema))
                    for element in tree.getroot().findall("{http://www.w3.org/2001/XMLSchema}import"):
                        if element.get("namespace") in setup_schemas.LOCAL_IMPORTS:
                            element.set("schemaLocation", "https://invalid.example/missing.xsd")
                    archive.writestr(schema.name, xsd_validator.etree.tostring(tree))
            outer_bytes = io.BytesIO()
            with zipfile.ZipFile(outer_bytes, "w") as archive:
                archive.writestr(inner_name, inner_bytes.getvalue())
            return outer_bytes.getvalue()

        downloads = {
            setup_schemas.ECMA_PART4_URL: nested_archive(
                self.schemas / "ooxml", "OfficeOpenXML-XMLSchema-Transitional.zip"
            ),
            setup_schemas.ECMA_PART2_URL: nested_archive(
                self.schemas / "opc", "OpenPackagingConventions-XMLSchema.zip"
            ),
        }
        for name in ("dc.xsd", "dcterms.xsd", "dcmitype.xsd"):
            downloads[setup_schemas.DUBLIN_CORE_URL + name] = (self.schemas / "opc" / name).read_bytes()
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(setup_schemas, "download", side_effect=downloads.__getitem__):
                self.assertTrue(setup_schemas.setup_schemas(Path(directory)))
            self.assertEqual(xsd_validator.check_schemas(Path(directory)), [])
            with patch.object(setup_schemas, "download", side_effect=downloads.__getitem__):
                with patch.object(setup_schemas, "check_schemas", return_value=["broken schema"]):
                    self.assertFalse(setup_schemas.setup_schemas(Path(directory)))


class PreviewTests(unittest.TestCase):
    def test_exit_zero_without_pdf_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.docx"
            source.touch()
            result = subprocess.CompletedProcess([], 0, "", "Error: source file could not be loaded")
            with patch("soffice_wrapper.run_soffice", return_value=result):
                with self.assertRaisesRegex(RuntimeError, "No usable PDF"):
                    office_readiness.convert_preview(source, root, "writer_pdf_Export")

    def test_timeout_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("soffice_wrapper.run_soffice", side_effect=subprocess.TimeoutExpired("soffice", 60)):
                with self.assertRaises(subprocess.TimeoutExpired):
                    office_readiness.convert_preview(root / "input.docx", root, "writer_pdf_Export")

    def test_non_pdf_output_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def invalid_conversion(*arguments, **keywords):
                (root / "input/input.pdf").write_text("not a PDF")
                return subprocess.CompletedProcess([], 0, "", "")

            with patch("soffice_wrapper.run_soffice", side_effect=invalid_conversion):
                with self.assertRaises(subprocess.CalledProcessError):
                    office_readiness.convert_preview(root / "input.docx", root, "writer_pdf_Export")


if __name__ == "__main__":
    unittest.main()