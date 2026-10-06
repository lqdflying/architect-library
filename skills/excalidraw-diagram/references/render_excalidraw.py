"""Render Excalidraw JSON to PNG using Playwright + headless Chromium.

Usage:
    cd <installed-skills-root>/excalidraw-diagram/references
    uv run python render_excalidraw.py <path-to-file.excalidraw> [--output path.png] [--scale 2]

The PNG stays at or below MAX_VIEW_PATCHES (under the 30,000-patch vision
reject limit). --scale is a requested supersample; it is reduced when the
full-size image would exceed that budget.

First-time setup:
    cd <installed-skills-root>/excalidraw-diagram/references
    bash install_deps.sh

Network note:
    Rendering needs the Excalidraw library. By default it is fetched from
    esm.sh at render time. For offline rendering, build the local bundle once
    (see README.md "Offline rendering" or run scripts/vendor_excalidraw.sh from
    the repository root) so it loads from references/vendor/excalidraw.bundle.mjs.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import json
import math
import socketserver
import struct
import sys
import threading
from pathlib import Path
from urllib.parse import urlparse

# Vision requests count ceil(width/32) * ceil(height/32) patches and reject
# an image above 30,000 after processing. They do not shrink it to fit.
# 29,000 leaves slack for a screenshot that is a few pixels larger than asked.
PATCH_PX = 32
PATCH_LIMIT = 30_000
MAX_VIEW_PATCHES = 29_000


@contextlib.contextmanager
def _serve_references(directory: Path):
    """Serve references/ over HTTP so ES module imports work (file:// blocks them)."""
    directory = directory.resolve()
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler,
        directory=str(directory),
    )
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as httpd:
        port = httpd.server_address[1]
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{port}"
        finally:
            httpd.shutdown()
            thread.join(timeout=5)


def validate_excalidraw(data: dict) -> list[str]:
    """Validate Excalidraw JSON structure. Returns list of errors (empty = valid)."""
    errors: list[str] = []

    if data.get("type") != "excalidraw":
        errors.append(f"Expected type 'excalidraw', got '{data.get('type')}'")

    if "elements" not in data:
        errors.append("Missing 'elements' array")
    elif not isinstance(data["elements"], list):
        errors.append("'elements' must be an array")
    elif len(data["elements"]) == 0:
        errors.append("'elements' array is empty — nothing to render")

    return errors


def patch_count(width: int, height: int) -> int:
    """32px patches needed to cover an image. A patch may hang past the edge."""
    if width <= 0 or height <= 0:
        return 0
    return math.ceil(width / PATCH_PX) * math.ceil(height / PATCH_PX)


def fit_view_size(
    css_w: float,
    css_h: float,
    requested_scale: float,
    max_patches: int = MAX_VIEW_PATCHES,
) -> tuple[int, int]:
    """Largest pixel size at or under requested_scale that stays within max_patches.

    Aspect ratio is preserved aside from flooring each side to a whole pixel.
    """
    if css_w <= 0 or css_h <= 0:
        raise ValueError(f"SVG size must be positive, got {css_w}x{css_h}")
    if requested_scale <= 0:
        raise ValueError(f"scale must be positive, got {requested_scale}")
    if max_patches < 1:
        raise ValueError(f"max_patches must be positive, got {max_patches}")

    max_w = max(1, math.floor(css_w * requested_scale))
    max_h = max(1, math.floor(css_h * requested_scale))
    if patch_count(max_w, max_h) <= max_patches:
        return max_w, max_h

    best = (1, 1)
    lo, hi = 0.0, 1.0
    for _ in range(48):
        mid = (lo + hi) / 2.0
        width = max(1, math.floor(max_w * mid))
        height = max(1, math.floor(max_h * mid))
        if patch_count(width, height) <= max_patches:
            best = (width, height)
            lo = mid
        else:
            hi = mid
    return best


def _parse_px(value: object) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"missing SVG size: {value!r}")
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text.endswith("px"):
        text = text[:-2].strip()
    return float(text)


def _png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"Not a PNG: {path}")
        handle.read(4)
        chunk_type = handle.read(4)
        if chunk_type != b"IHDR":
            raise ValueError(f"PNG missing IHDR: {path}")
        width, height = struct.unpack(">II", handle.read(8))
    return width, height


def _report_png(width: int, height: int, requested_w: int, requested_h: int, max_patches: int) -> None:
    patches = patch_count(width, height)
    requested_patches = patch_count(requested_w, requested_h)
    if requested_patches <= max_patches:
        print(
            f"rendered {width}x{height} ({patches} patches, limit {max_patches})",
            file=sys.stderr,
        )
        return
    print(
        f"capped PNG to {width}x{height} ({patches} patches, limit {max_patches}); "
        f"requested scale would have produced {requested_w}x{requested_h} "
        f"({requested_patches} patches)",
        file=sys.stderr,
    )


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: float = 2,
    max_patches: int = MAX_VIEW_PATCHES,
) -> Path:
    """Render an .excalidraw file to PNG. Returns the output PNG path."""
    # Import playwright here so validation errors show before import errors
    try:
        from playwright.sync_api import sync_playwright
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        print(
            "Run: cd <installed-skills-root>/excalidraw-diagram/references "
            "&& bash install_deps.sh",
            file=sys.stderr,
        )
        sys.exit(1)

    # Read and validate
    raw = excalidraw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {excalidraw_path}: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print(f"ERROR: Invalid Excalidraw file:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Output path
    if output_path is None:
        output_path = excalidraw_path.with_suffix(".png")

    refs_dir = Path(__file__).parent
    template_path = refs_dir / "render_template.html"
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    vendor_bundle = refs_dir / "vendor" / "excalidraw.bundle.mjs"

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            if "Executable doesn't exist" in str(e) or "browserType.launch" in str(e):
                print("ERROR: Chromium not installed for Playwright.", file=sys.stderr)
                print(
                    "Run: cd <installed-skills-root>/excalidraw-diagram/references "
                    "&& uv run python -m playwright install chromium",
                    file=sys.stderr,
                )
                sys.exit(1)
            raise

        # Pixel size is applied on the SVG after export. device_scale_factor
        # stays 1 so a requested --scale is not applied twice. The viewport
        # does not clip an element screenshot.
        page = browser.new_page(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
        )

        # Load template via local HTTP — file:// URLs break dynamic import() of the
        # vendored ESM bundle; a loopback server serves references/ including vendor/.
        with _serve_references(refs_dir) as base_url:
            template_url = f"{base_url}/render_template.html"
            if vendor_bundle.is_file():

                def _block_remote(route) -> None:
                    url = route.request.url
                    if url.startswith(("http://", "https://")):
                        host = urlparse(url).hostname
                        if host in ("127.0.0.1", "localhost", "::1"):
                            route.continue_()
                        else:
                            route.abort()
                    else:
                        route.continue_()

                page.route("**/*", _block_remote)

            page.goto(template_url)

            # Wait for the ES module to load (imports the Excalidraw library)
            try:
                page.wait_for_function("window.__moduleReady === true", timeout=30000)
            except PlaywrightTimeoutError:
                module_error = page.evaluate("window.__moduleError || null")
                print(
                    "ERROR: Could not load the Excalidraw library in the browser.",
                    file=sys.stderr,
                )
                if module_error:
                    print(f"  {module_error}", file=sys.stderr)
                if vendor_bundle.is_file():
                    print(
                        "A vendor bundle exists but failed to load. Rebuild with:",
                        file=sys.stderr,
                    )
                    print("  bash scripts/vendor_excalidraw.sh", file=sys.stderr)
                else:
                    print(
                        "Build the offline bundle: bash scripts/vendor_excalidraw.sh",
                        file=sys.stderr,
                    )
                    print("Or allow network access to esm.sh for CDN fallback.", file=sys.stderr)
                browser.close()
                sys.exit(1)

            # Inject the diagram data and render. Pass `data` as an argument rather
            # than interpolating JSON into the expression so values containing JS
            # line terminators (U+2028 / U+2029) can't break the call.
            result = page.evaluate("data => window.renderDiagram(data)", data)

            if not result or not result.get("success"):
                error_msg = (
                    result.get("error", "Unknown render error")
                    if result
                    else "renderDiagram returned null"
                )
                print(f"ERROR: Render failed: {error_msg}", file=sys.stderr)
                browser.close()
                sys.exit(1)

            # Wait for render completion signal
            page.wait_for_function("window.__renderComplete === true", timeout=15000)

            svg_el = page.query_selector("#root svg")
            if svg_el is None:
                print("ERROR: No SVG element found after render.", file=sys.stderr)
                browser.close()
                sys.exit(1)

            try:
                css_w = _parse_px(result.get("width"))
                css_h = _parse_px(result.get("height"))
            except (TypeError, ValueError):
                box = svg_el.bounding_box()
                if not box or box["width"] <= 0 or box["height"] <= 0:
                    print("ERROR: Could not read SVG size.", file=sys.stderr)
                    browser.close()
                    sys.exit(1)
                css_w = float(box["width"])
                css_h = float(box["height"])

            view_w, view_h = fit_view_size(css_w, css_h, scale, max_patches)
            requested_w = max(1, math.floor(css_w * scale))
            requested_h = max(1, math.floor(css_h * scale))

            # Re-measure after the screenshot. If the bitmap is still over the
            # budget (padding, DPR), shrink and shoot again.
            for _ in range(3):
                page.evaluate(
                    """({width, height}) => {
                        const svg = document.querySelector('#root svg');
                        const root = document.getElementById('root');
                        svg.setAttribute('width', String(width));
                        svg.setAttribute('height', String(height));
                        svg.style.width = width + 'px';
                        svg.style.height = height + 'px';
                        if (root) {
                            root.style.width = width + 'px';
                            root.style.height = height + 'px';
                        }
                    }""",
                    {"width": view_w, "height": view_h},
                )
                svg_el.screenshot(path=str(output_path))
                actual_w, actual_h = _png_size(output_path)
                if patch_count(actual_w, actual_h) <= max_patches:
                    _report_png(actual_w, actual_h, requested_w, requested_h, max_patches)
                    break
                shrink = math.sqrt(max_patches / patch_count(actual_w, actual_h)) * 0.98
                view_w = max(1, math.floor(actual_w * shrink))
                view_h = max(1, math.floor(actual_h * shrink))
            else:
                actual_w, actual_h = _png_size(output_path)
                print(
                    f"ERROR: PNG {actual_w}x{actual_h} is still "
                    f"{patch_count(actual_w, actual_h)} patches "
                    f"(limit {max_patches}).",
                    file=sys.stderr,
                )
                browser.close()
                sys.exit(1)

        browser.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Excalidraw JSON to PNG")
    parser.add_argument("input", type=Path, help="Path to .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output PNG path (default: same name with .png)")
    parser.add_argument(
        "--scale",
        "-s",
        type=float,
        default=2,
        help="Requested render scale (default: 2). Reduced when the PNG would exceed the vision patch limit.",
    )
    parser.add_argument(
        "--max-patches",
        type=int,
        default=MAX_VIEW_PATCHES,
        help=f"Max 32px patches in the PNG (default: {MAX_VIEW_PATCHES}; APIs reject above {PATCH_LIMIT})",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    if args.scale <= 0:
        print(f"ERROR: --scale must be positive, got {args.scale}", file=sys.stderr)
        sys.exit(1)
    if args.max_patches < 1 or args.max_patches > PATCH_LIMIT:
        print(
            f"ERROR: --max-patches must be from 1 to {PATCH_LIMIT}, got {args.max_patches}",
            file=sys.stderr,
        )
        sys.exit(1)

    png_path = render(args.input, args.output, args.scale, args.max_patches)
    print(str(png_path))


if __name__ == "__main__":
    main()
