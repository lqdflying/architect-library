"""Search the bundled vendor SVGs and embed them into existing image nodes."""

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import time
from xml.etree import ElementTree


CACHE = Path(__file__).resolve().parent.parent / "assets" / "vendors"
ASPECT_TOLERANCE = 0.02

_spec = importlib.util.spec_from_file_location("excalidraw_azure_icons", Path(__file__).with_name("azure_icons.py"))
azure_icons = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(azure_icons)


def load_cache():
    manifest = json.loads((CACHE / "manifest.json").read_text(encoding="utf-8"))
    if not (CACHE / manifest["terms"]).is_file():
        raise ValueError("Vendor icon terms note is missing")
    for icon in manifest["icons"]:
        path = (CACHE / icon["file"]).resolve()
        if path.parent != CACHE.resolve() or hashlib.sha256(path.read_bytes()).hexdigest() != icon["sha256"]:
            raise ValueError(f"Vendor icon cache checksum mismatch: {icon['file']}")
    return manifest


def search_icons(query):
    manifest = load_cache()
    terms = re.findall(r"[a-z0-9]+", query.lower())
    matches = []
    for icon in manifest["icons"]:
        haystack = f"{icon['file']} {icon['title']}".lower()
        if all(term in haystack for term in terms):
            matches.append(icon["file"])
    return sorted(matches)


def with_brand_fill(svg, hex_color):
    if not re.fullmatch(r"[0-9A-F]{6}", hex_color):
        raise ValueError(f"Invalid brand color: {hex_color}")
    try:
        text = svg.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("Cached SVG is not UTF-8") from error
    if not text.startswith("<svg ") or " fill=" in text:
        raise ValueError("Cached SVG must stay an unmodified Simple Icons file with no fill")
    return text.replace("<svg ", f'<svg fill="#{hex_color}" ', 1).encode("utf-8")


def path_data(svg):
    return [element.get("d") for element in ElementTree.fromstring(svg).iter() if element.tag.endswith("path")]


def embed_icons(diagram, selections):
    scene = json.loads(diagram.read_text(encoding="utf-8"))
    if scene.get("type") != "excalidraw" or not isinstance(scene.get("elements"), list):
        raise ValueError("Expected an Excalidraw scene with an elements array")
    elements = {element["id"]: element for element in scene["elements"]}
    if len(elements) != len(scene["elements"]):
        raise ValueError("Duplicate element IDs")
    files = scene.setdefault("files", {})
    manifest = load_cache()
    by_file = {icon["file"]: icon for icon in manifest["icons"]}
    timestamp = int(time.time() * 1000)
    selected_ids = set()
    changed = []
    for selection in selections:
        element_id, separator, name = selection.partition("=")
        icon = by_file.get(name)
        if not separator or icon is None:
            raise ValueError(f"Use IMAGE_ID=EXACT_PATH from search; invalid selection: {selection}")
        if element_id in selected_ids:
            raise ValueError(f"Image selected more than once: {element_id}")
        selected_ids.add(element_id)
        element = elements.get(element_id)
        if not element or element.get("isDeleted") or element["type"] != "image":
            raise ValueError(f"Expected an existing, non-deleted image node: {element_id}")
        svg = (CACHE / icon["file"]).read_bytes()
        ratio = azure_icons.svg_aspect(svg)
        width, height = element.get("width") or 0, element.get("height") or 0
        if width <= 0 or height <= 0 or abs(width / height / ratio - 1) > ASPECT_TOLERANCE:
            raise ValueError(f"Image {element_id} is {width}x{height}; resize it to the icon's width/height ratio {ratio:.3f}")
        filled = with_brand_fill(svg, icon["hex"])
        if path_data(filled) != path_data(svg):
            raise ValueError(f"Brand fill changed path data: {name}")
        file_id = "vendor-" + manifest["version"] + "-" + hashlib.sha256(filled).hexdigest()
        data_url = "data:image/svg+xml;base64," + base64.b64encode(filled).decode("ascii")
        existing = files.get(file_id)
        if existing and (existing.get("dataURL") != data_url or existing.get("mimeType") != "image/svg+xml"):
            raise ValueError(f"Conflicting embedded asset: {file_id}")
        if existing is None:
            files[file_id] = {"id": file_id, "mimeType": "image/svg+xml", "dataURL": data_url, "created": timestamp, "lastRetrieved": timestamp}
        if existing is None or element.get("fileId") != file_id or element.get("status") != "saved":
            element["fileId"] = file_id
            element["status"] = "saved"
            element["version"] = element.get("version", 0) + 1
            element["updated"] = timestamp
            changed.append(element_id)
    if changed:
        azure_icons.write_scene(diagram, scene)
    return changed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    search = commands.add_parser("search", help="List exact SVG paths in the offline cache")
    search.add_argument("query", nargs="?", default="")
    embed = commands.add_parser("embed", help="Embed selected SVGs without changing node geometry")
    embed.add_argument("diagram", type=Path)
    embed.add_argument("--icon", action="append", required=True, metavar="IMAGE_ID=SVG_PATH")
    arguments = parser.parse_args()
    try:
        if arguments.command == "search":
            matches = search_icons(arguments.query)
            print("\n".join(matches))
            return 0 if matches else 1
        changed = embed_icons(arguments.diagram, arguments.icon)
        print(json.dumps({"diagram": str(arguments.diagram), "updatedImages": changed, "networkUsed": False}))
        return 0
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
