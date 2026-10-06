import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile


spec = importlib.util.spec_from_file_location("azure_icons", Path(__file__).with_name("azure_icons.py"))
azure_icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(azure_icons)
DATABRICKS = "analytics/10787-icon-service-Azure-Databricks.svg"
PRIVATE_ENDPOINT = "other/02579-icon-service-Private-Endpoints.svg"
APPLIED_AI = "ai + machine learning/02749-icon-service-Azure-Applied-AI-Services.svg"


class AzureIconTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "diagram.excalidraw"
        self.scene = {
            "type": "excalidraw", "version": 2, "appState": {"gridSize": 20},
            "files": {"unrelated": {"dataURL": "retained"}},
            "elements": [
                {"id": "workspace", "type": "image", "x": 20, "y": 40, "width": 64, "height": 64, "fileId": "old", "status": "pending", "version": 2, "boundElements": [{"id": "link", "type": "arrow"}]},
                {"id": "endpoint", "type": "image", "x": 120, "y": 40, "width": 64, "height": 64, "version": 1, "boundElements": [{"id": "link", "type": "arrow"}]},
                {"id": "link", "type": "arrow", "startBinding": {"elementId": "workspace"}, "endBinding": {"elementId": "endpoint"}, "points": [[0, 0], [36, 0]]},
                {"id": "caption", "type": "text", "text": "Workspace", "x": 20, "y": 10},
            ],
        }
        self.write_scene()

    def write_scene(self):
        self.path.write_text(json.dumps(self.scene) + "\n", encoding="utf-8")

    def test_search_offline(self):
        self.assertEqual(azure_icons.search_icons("Databricks"), [DATABRICKS])
        self.assertEqual(azure_icons.search_icons("Private Endpoints"), [PRIVATE_ENDPOINT])
        self.assertEqual(azure_icons.search_icons("not-an-azure-service-123456"), [])

    def test_search_prefers_service_names_over_categories(self):
        matches = azure_icons.search_icons("Virtual Network")
        self.assertIn("networking/10061-icon-service-Virtual-Networks.svg", matches)
        self.assertNotIn("networking/00860-icon-service-Virtual-WAN-Hub.svg", matches)
        category = azure_icons.search_icons("networking")
        self.assertGreater(len(category), 10)
        self.assertTrue(all(name.startswith("networking/") for name in category))

    def test_embed_preserves_geometry_bindings_and_unrelated_data(self):
        original = copy.deepcopy(self.scene)
        self.assertEqual(azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}", f"endpoint={PRIVATE_ENDPOINT}"]), ["workspace", "endpoint"])
        result = json.loads(self.path.read_text())
        self.assertEqual(result["appState"], original["appState"])
        self.assertEqual(result["files"]["unrelated"], original["files"]["unrelated"])
        self.assertEqual(result["elements"][2:], original["elements"][2:])
        for previous, updated in zip(original["elements"][:2], result["elements"][:2]):
            for key in ("id", "type", "x", "y", "width", "height", "boundElements"):
                self.assertEqual(updated[key], previous[key])
        manifest, archive = azure_icons.load_cache()
        with archive:
            for element, name in zip(result["elements"][:2], (DATABRICKS, PRIVATE_ENDPOINT)):
                svg = base64.b64decode(result["files"][element["fileId"]]["dataURL"].split(",", 1)[1], validate=True)
                self.assertEqual(svg, archive.read(manifest["prefix"] + name))

    def test_repeat_is_byte_for_byte_noop(self):
        selection = [f"workspace={DATABRICKS}"]
        azure_icons.embed_icons(self.path, selection)
        before = self.path.read_bytes()
        self.assertEqual(azure_icons.embed_icons(self.path, selection), [])
        self.assertEqual(self.path.read_bytes(), before)

    def test_missing_embedded_file_is_restored(self):
        selection = [f"workspace={DATABRICKS}"]
        azure_icons.embed_icons(self.path, selection)
        self.scene = json.loads(self.path.read_text())
        del self.scene["files"][self.scene["elements"][0]["fileId"]]
        self.write_scene()
        self.assertEqual(azure_icons.embed_icons(self.path, selection), ["workspace"])
        result = json.loads(self.path.read_text())
        self.assertIn(result["elements"][0]["fileId"], result["files"])

    def test_invalid_batch_does_not_write(self):
        for invalid in (f"missing={DATABRICKS}", f"caption={DATABRICKS}", "endpoint=../../file.svg", f"workspace={PRIVATE_ENDPOINT}"):
            with self.subTest(invalid=invalid):
                before = self.path.read_bytes()
                with self.assertRaises(ValueError):
                    azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}", invalid])
                self.assertEqual(self.path.read_bytes(), before)

    def test_deleted_image_is_rejected(self):
        self.scene["elements"][0]["isDeleted"] = True
        self.write_scene()
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_file_id_collision_is_rejected(self):
        manifest, archive = azure_icons.load_cache()
        with archive:
            svg = archive.read(manifest["prefix"] + DATABRICKS)
        file_id = "azure-" + manifest["version"].lower() + "-" + hashlib.sha256(svg).hexdigest()
        self.scene["files"][file_id] = {"dataURL": "other-artwork", "mimeType": "image/svg+xml"}
        self.write_scene()
        before = self.path.read_bytes()
        with self.assertRaises(ValueError):
            azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}"])
        self.assertEqual(self.path.read_bytes(), before)

    def test_distorting_dimensions_are_rejected(self):
        for width, height, name in ((64, 32, DATABRICKS), (64, 64, APPLIED_AI), (0, 64, DATABRICKS)):
            with self.subTest(width=width, height=height, name=name):
                self.scene["elements"][0].update(width=width, height=height)
                self.write_scene()
                before = self.path.read_bytes()
                with self.assertRaisesRegex(ValueError, "ratio"):
                    azure_icons.embed_icons(self.path, [f"workspace={name}"])
                self.assertEqual(self.path.read_bytes(), before)

    def test_non_square_icon_at_its_own_ratio_is_accepted(self):
        manifest, archive = azure_icons.load_cache()
        with archive:
            ratio = azure_icons.svg_aspect(archive.read(manifest["prefix"] + APPLIED_AI))
        self.assertNotAlmostEqual(ratio, 1, places=1)
        self.scene["elements"][0].update(width=round(64 * ratio, 2), height=64)
        self.write_scene()
        self.assertEqual(azure_icons.embed_icons(self.path, [f"workspace={APPLIED_AI}"]), ["workspace"])

    def test_failed_write_keeps_original_and_leaves_no_temporary_file(self):
        before = self.path.read_bytes()
        with patch.object(azure_icons.os, "replace", side_effect=OSError("disk full")), self.assertRaises(OSError):
            azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}"])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in self.path.parent.iterdir()), [self.path.name])

    def test_write_preserves_file_mode(self):
        self.path.chmod(0o640)
        azure_icons.embed_icons(self.path, [f"workspace={DATABRICKS}"])
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o640)
        self.assertEqual(sorted(path.name for path in self.path.parent.iterdir()), [self.path.name])

    def test_corrupt_cache_is_rejected(self):
        cache = Path(self.temporary.name) / "cache"
        cache.mkdir()
        (cache / "manifest.json").write_text(json.dumps({"archive": "icons.zip", "sha256": "0" * 64}))
        (cache / "icons.zip").write_bytes(b"corrupt")
        with patch.object(azure_icons, "CACHE", cache), self.assertRaisesRegex(ValueError, "checksum mismatch"):
            azure_icons.search_icons("Databricks")

    def test_archive_retains_official_terms(self):
        manifest, archive = azure_icons.load_cache()
        with archive:
            self.assertIn(manifest["terms_member"], archive.namelist())
            self.assertGreater(len(azure_icons.icon_names(archive, manifest["prefix"])), 100)
            self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()