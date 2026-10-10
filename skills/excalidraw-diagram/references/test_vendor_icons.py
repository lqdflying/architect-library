import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from xml.etree import ElementTree


spec = importlib.util.spec_from_file_location("vendor_icons", Path(__file__).with_name("vendor_icons.py"))
vendor_icons = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vendor_icons)
F5 = "f5.svg"
DATADOG = "datadog.svg"


def root_fill(svg):
    root = ElementTree.fromstring(svg)
    return root.get("fill")


class VendorIconTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "diagram.excalidraw"
        self.scene = {
            "type": "excalidraw", "version": 2, "appState": {"gridSize": 20},
            "files": {"unrelated": {"dataURL": "retained"}},
            "elements": [
                {"id": "edge", "type": "image", "x": 20, "y": 40, "width": 64, "height": 64, "fileId": "old", "status": "pending", "version": 2, "boundElements": [{"id": "link", "type": "arrow"}]},
                {"id": "monitor", "type": "image", "x": 120, "y": 40, "width": 64, "height": 64, "version": 1, "boundElements": [{"id": "link", "type": "arrow"}]},
                {"id": "link", "type": "arrow", "startBinding": {"elementId": "edge"}, "endBinding": {"elementId": "monitor"}, "points": [[0, 0], [36, 0]]},
                {"id": "caption", "type": "text", "text": "F5", "x": 20, "y": 10},
            ],
        }
        self.write_scene()

    def write_scene(self):
        self.path.write_text(json.dumps(self.scene) + "\n", encoding="utf-8")

    def test_search_offline(self):
        self.assertEqual(vendor_icons.search_icons("F5"), [F5])
        self.assertEqual(vendor_icons.search_icons("Palo Alto Networks"), ["paloaltonetworks.svg"])
        self.assertEqual(vendor_icons.search_icons("nginx"), ["nginx.svg"])
        self.assertEqual(vendor_icons.search_icons("Datadog"), [DATADOG])
        self.assertEqual(vendor_icons.search_icons("not-a-vendor-123456"), [])

    def test_cache_checksums_match_manifest(self):
        manifest = vendor_icons.load_cache()
        self.assertEqual(manifest["version"], "16.0.0")
        self.assertEqual([icon["file"] for icon in manifest["icons"]], ["datadog.svg", "f5.svg", "nginx.svg", "paloaltonetworks.svg"])
        self.assertTrue((vendor_icons.CACHE / manifest["terms"]).is_file())
        for icon in manifest["icons"]:
            blob = (vendor_icons.CACHE / icon["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(blob).hexdigest(), icon["sha256"])
            self.assertNotIn(b" fill=", blob)
            self.assertEqual(vendor_icons.azure_icons.svg_aspect(blob), 1)

    def test_corrupt_cache_is_rejected(self):
        cache = Path(self.temporary.name) / "cache"
        cache.mkdir()
        (cache / "manifest.json").write_text(json.dumps({
            "version": "16.0.0", "terms": "TERMS.md",
            "icons": [{"file": "f5.svg", "title": "F5", "hex": "E4002B", "sha256": "0" * 64}],
        }))
        (cache / "TERMS.md").write_text("terms\n", encoding="utf-8")
        (cache / "f5.svg").write_bytes(b"<svg></svg>")
        with patch.object(vendor_icons, "CACHE", cache), self.assertRaisesRegex(ValueError, "checksum mismatch"):
            vendor_icons.search_icons("F5")

    def test_embed_preserves_geometry_and_injects_brand_fill(self):
        original = copy.deepcopy(self.scene)
        cache_before = {icon["file"]: (vendor_icons.CACHE / icon["file"]).read_bytes() for icon in vendor_icons.load_cache()["icons"]}
        self.assertEqual(vendor_icons.embed_icons(self.path, [f"edge={F5}", f"monitor={DATADOG}"]), ["edge", "monitor"])
        result = json.loads(self.path.read_text())
        self.assertEqual(result["appState"], original["appState"])
        self.assertEqual(result["files"]["unrelated"], original["files"]["unrelated"])
        self.assertEqual(result["elements"][2:], original["elements"][2:])
        manifest = vendor_icons.load_cache()
        colors = {icon["file"]: icon["hex"] for icon in manifest["icons"]}
        for previous, updated, name in zip(original["elements"][:2], result["elements"][:2], (F5, DATADOG)):
            for key in ("id", "type", "x", "y", "width", "height", "boundElements"):
                self.assertEqual(updated[key], previous[key])
            filled = base64.b64decode(result["files"][updated["fileId"]]["dataURL"].split(",", 1)[1], validate=True)
            cached = cache_before[name]
            self.assertEqual(vendor_icons.path_data(filled), vendor_icons.path_data(cached))
            self.assertEqual(root_fill(filled), f"#{colors[name]}")
            self.assertEqual(updated["fileId"], "vendor-" + manifest["version"] + "-" + hashlib.sha256(filled).hexdigest())
            self.assertEqual((vendor_icons.CACHE / name).read_bytes(), cached)

    def test_repeat_is_byte_for_byte_noop(self):
        selection = [f"edge={F5}"]
        vendor_icons.embed_icons(self.path, selection)
        before = self.path.read_bytes()
        self.assertEqual(vendor_icons.embed_icons(self.path, selection), [])
        self.assertEqual(self.path.read_bytes(), before)

    def test_distorting_dimensions_are_rejected(self):
        for width, height in ((64, 32), (0, 64)):
            with self.subTest(width=width, height=height):
                self.scene["elements"][0].update(width=width, height=height)
                self.write_scene()
                before = self.path.read_bytes()
                with self.assertRaisesRegex(ValueError, "ratio"):
                    vendor_icons.embed_icons(self.path, [f"edge={F5}"])
                self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_batch_does_not_write(self):
        for invalid in (f"missing={F5}", f"caption={F5}", "monitor=../../file.svg"):
            with self.subTest(invalid=invalid):
                before = self.path.read_bytes()
                with self.assertRaises(ValueError):
                    vendor_icons.embed_icons(self.path, [f"edge={F5}", invalid])
                self.assertEqual(self.path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
