"""Search the bundled Azure SVG archive and embed assets into existing image nodes."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import time
from xml.etree import ElementTree
import zipfile


CACHE = Path(__file__).resolve().parent.parent / "assets" / "azure"
ASPECT_TOLERANCE = 0.02


def load_cache():
    manifest = json.loads((CACHE / "manifest.json").read_text(encoding="utf-8"))
    archive_path = CACHE / manifest["archive"]
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Azure icon cache checksum mismatch; restore or explicitly refresh the pinned archive")
    return manifest, zipfile.ZipFile(archive_path)


def icon_names(archive, prefix):
    return sorted(name[len(prefix):] for name in archive.namelist() if name.startswith(prefix) and name.lower().endswith(".svg"))


def search_icons(query):
    manifest, archive = load_cache()
    terms = re.findall(r"[a-z0-9]+", query.lower())
    with archive:
        names = icon_names(archive, manifest["prefix"])
    # Match service file names first so "network" does not pull in every icon under networking/.
    by_service = [name for name in names if all(term in name.rsplit("/", 1)[-1].lower() for term in terms)]
    return by_service or [name for name in names if all(term in name.lower() for term in terms)]


def svg_aspect(svg):
    root = ElementTree.fromstring(svg)
    sizes = re.split(r"[\s,]+", root.get("viewBox", "").strip())[2:4] or [root.get("width", ""), root.get("height", "")]
    try:
        width, height = (float(size.removesuffix("px")) for size in sizes)
        return width / height
    except (ValueError, ZeroDivisionError):
        raise ValueError("SVG has no usable viewBox or width/height") from None


def write_scene(diagram, scene):
    target = diagram.resolve()
    descriptor, temporary = tempfile.mkstemp(dir=target.parent, prefix=f".{target.name}.", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(scene, indent=2, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, stat.S_IMODE(target.stat().st_mode))
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)


def embed_icons(diagram, selections):
    scene = json.loads(diagram.read_text(encoding="utf-8"))
    if scene.get("type") != "excalidraw" or not isinstance(scene.get("elements"), list):
        raise ValueError("Expected an Excalidraw scene with an elements array")
    elements = {element["id"]: element for element in scene["elements"]}
    if len(elements) != len(scene["elements"]):
        raise ValueError("Duplicate element IDs")
    files = scene.setdefault("files", {})
    manifest, archive = load_cache()
    timestamp = int(time.time() * 1000)
    selected_ids = set()
    changed = []
    with archive:
        available = set(icon_names(archive, manifest["prefix"]))
        for selection in selections:
            element_id, separator, name = selection.partition("=")
            if not separator or name not in available:
                raise ValueError(f"Use IMAGE_ID=EXACT_PATH from search; invalid selection: {selection}")
            if element_id in selected_ids:
                raise ValueError(f"Image selected more than once: {element_id}")
            selected_ids.add(element_id)
            element = elements.get(element_id)
            if not element or element.get("isDeleted") or element["type"] != "image":
                raise ValueError(f"Expected an existing, non-deleted image node: {element_id}")
            svg = archive.read(manifest["prefix"] + name)
            ratio = svg_aspect(svg)
            width, height = element.get("width") or 0, element.get("height") or 0
            if width <= 0 or height <= 0 or abs(width / height / ratio - 1) > ASPECT_TOLERANCE:
                raise ValueError(f"Image {element_id} is {width}x{height}; resize it to the icon's width/height ratio {ratio:.3f}")
            file_id = "azure-" + manifest["version"].lower() + "-" + hashlib.sha256(svg).hexdigest()
            data_url = "data:image/svg+xml;base64," + base64.b64encode(svg).decode("ascii")
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
        write_scene(diagram, scene)
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
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())