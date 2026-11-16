import tempfile
import unittest
import zipfile
from pathlib import Path

from lxml import etree
from openpyxl import Workbook
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

import share_strings
import xsd_validator


class ShareStringsTests(unittest.TestCase):
    def workbook(self, directory):
        path = Path(directory) / "book.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Model"
        sheet["A1"] = "Hello"
        sheet["A1"].hyperlink = "https://example.com"
        sheet["B1"] = "Hello"
        sheet["C1"] = "=SUM(1,2)"
        sheet["D1"] = 4
        sheet["E1"] = "A & B"
        sheet["F1"] = " Hello"
        other = workbook.create_sheet("Other")
        other["A1"] = "There"
        other["B1"] = CellRichText(TextBlock(InlineFont(b=True), "Bold"), " tail")
        workbook.save(path)
        workbook.close()
        return path

    def sheet_text(self, path, name):
        with zipfile.ZipFile(path) as archive:
            return archive.read(name).decode()

    def test_text_cells_become_shared_strings_on_every_sheet(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.workbook(directory)
            before = set(zipfile.ZipFile(path).namelist())
            result = share_strings.share_strings(path)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["inline_strings"], 0)
            self.assertEqual(result["text_cells"], 6)
            self.assertTrue(result["shared_string_part"])
            self.assertEqual(result["converted"], 6)

            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
                for member in names:
                    archive.read(member)
                shared = archive.read("xl/sharedStrings.xml").decode()
            self.assertEqual(names, before | {"xl/sharedStrings.xml"})
            self.assertNotIn("inlineStr", self.sheet_text(path, "xl/worksheets/sheet1.xml"))
            self.assertNotIn("inlineStr", self.sheet_text(path, "xl/worksheets/sheet2.xml"))
            self.assertEqual(self.sheet_text(path, "xl/worksheets/sheet1.xml").count('t="s"'), 4)
            self.assertIn("<v>0</v>", self.sheet_text(path, "xl/worksheets/sheet1.xml"))
            self.assertEqual(shared.count("<si>"), 5)

            workbook = share_strings_load(path)
            sheet = workbook["Model"]
            self.assertEqual(sheet["A1"].value, "Hello")
            self.assertEqual(sheet["A1"].hyperlink.target, "https://example.com")
            self.assertEqual(sheet["B1"].value, "Hello")
            self.assertEqual(sheet["C1"].value, "=SUM(1,2)")
            self.assertEqual(sheet["D1"].value, 4)
            self.assertEqual(sheet["E1"].value, "A & B")
            self.assertEqual(sheet["F1"].value, " Hello")
            self.assertEqual(workbook["Other"]["A1"].value, "There")
            self.assertIn("Bold", str(workbook["Other"]["B1"].value))
            workbook.close()

            again = share_strings.share_strings(path)
            self.assertEqual(again["converted"], 0)
            self.assertEqual(again["inline_strings"], 0)
            self._assert_schema(path)

    def test_numbers_and_formulas_stay_untouched(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "numbers.xlsx"
            workbook = Workbook()
            sheet = workbook.active
            sheet["A1"] = 1
            sheet["B1"] = "=A1+1"
            workbook.save(path)
            workbook.close()
            original = path.read_bytes()
            result = share_strings.share_strings(path)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["text_cells"], 0)
            self.assertEqual(result["inline_strings"], 0)
            self.assertFalse(result["shared_string_part"])
            self.assertEqual(result["converted"], 0)
            self.assertEqual(path.read_bytes(), original)

    def test_openpyxl_edit_is_converted_again(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.workbook(directory)
            self.assertEqual(share_strings.share_strings(path)["status"], "success")
            workbook = share_strings_load(path)
            workbook["Model"]["A1"] = "Changed"
            workbook.save(path)
            workbook.close()
            self.assertIn("inlineStr", self.sheet_text(path, "xl/worksheets/sheet1.xml"))
            result = share_strings.share_strings(path)
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["inline_strings"], 0)
            self.assertGreater(result["text_cells"], 0)
            self.assertNotIn("inlineStr", self.sheet_text(path, "xl/worksheets/sheet1.xml"))
            self.assertNotIn("inlineStr", self.sheet_text(path, "xl/worksheets/sheet2.xml"))
            workbook = share_strings_load(path)
            self.assertEqual(workbook["Model"]["A1"].value, "Changed")
            self.assertEqual(workbook["Model"]["B1"].value, "Hello")
            self.assertEqual(workbook["Other"]["A1"].value, "There")
            workbook.close()

    def _assert_schema(self, path):
        schemas = xsd_validator._get_schemas_dir()
        self.assertIsNotNone(schemas)
        spreadsheet = xsd_validator.load_schema(schemas / "ooxml/sml.xsd")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with zipfile.ZipFile(path) as archive:
                archive.extractall(root)
            for relative in (
                "xl/worksheets/sheet1.xml",
                "xl/worksheets/sheet2.xml",
                "xl/sharedStrings.xml",
            ):
                document = etree.parse(str(root / relative))
                self.assertTrue(
                    spreadsheet.validate(document),
                    f"{relative}: {[err.message for err in spreadsheet.error_log]}",
                )
            for relative in ("[Content_Types].xml", "xl/_rels/workbook.xml.rels"):
                valid, errors = xsd_validator.validate_file_xsd(root / relative, schemas, root)
                self.assertTrue(valid, f"{relative}: {errors}")


def share_strings_load(path):
    from openpyxl import load_workbook

    return load_workbook(path)


if __name__ == "__main__":
    unittest.main()
