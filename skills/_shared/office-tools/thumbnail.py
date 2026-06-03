#!/usr/bin/env python3
"""Create thumbnail grids from PowerPoint slides for visual analysis.

Labels each thumbnail with its XML filename (slide1.xml, slide2.xml, ...).
Hidden slides shown with a placeholder pattern. Max 12 slides per grid.

Requires: Pillow, LibreOffice (soffice), Poppler (pdftoppm)

Usage:
    python thumbnail.py presentation.pptx
    python thumbnail.py template.pptx output_prefix --cols 4
    python thumbnail.py deck.pptx --per-slide /tmp/pptx-preview --dpi 150
    python thumbnail.py deck.pptx preview --per-slide ./slides --no-grid
"""

import argparse
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    import defusedxml.minidom as minidom_mod
except ImportError:
    import xml.dom.minidom as minidom_mod

from PIL import Image, ImageDraw, ImageFont

try:
    from soffice_wrapper import get_soffice_env
except ImportError:
    import os
    def get_soffice_env():
        return os.environ.copy()

THUMB_WIDTH = 300
DPI = 100
MAX_COLS = 6
DEFAULT_COLS = 3
JPEG_QUALITY = 95
PADDING = 20
BORDER = 2
FONT_RATIO = 0.10
LABEL_PAD_RATIO = 0.4


def get_slide_info(pptx_path: Path) -> list[dict]:
    """Extract ordered slide names and hidden status from PPTX."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        rels = minidom_mod.parseString(zf.read("ppt/_rels/presentation.xml.rels").decode("utf-8"))
        rid_to_slide = {}
        for rel in rels.getElementsByTagName("Relationship"):
            rid = rel.getAttribute("Id")
            target = rel.getAttribute("Target")
            rel_type = rel.getAttribute("Type")
            if "slide" in rel_type and target.startswith("slides/"):
                rid_to_slide[rid] = target.replace("slides/", "")

        pres = minidom_mod.parseString(zf.read("ppt/presentation.xml").decode("utf-8"))
        slides = []
        for sld_id in pres.getElementsByTagName("p:sldId"):
            rid = sld_id.getAttribute("r:id")
            if rid in rid_to_slide:
                hidden = sld_id.getAttribute("show") == "0"
                slides.append({"name": rid_to_slide[rid], "hidden": hidden})

    return slides


def convert_to_images(pptx_path: Path, temp_dir: Path, dpi: int = DPI) -> list[Path]:
    """Convert PPTX to PDF then to JPEG images."""
    pdf_path = temp_dir / f"{pptx_path.stem}.pdf"

    result = subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", "--outdir",
         str(temp_dir), str(pptx_path)],
        capture_output=True, text=True, env=get_soffice_env(),
    )
    if result.returncode != 0 or not pdf_path.exists():
        raise RuntimeError(f"PDF conversion failed: {result.stderr}")

    subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(dpi), str(pdf_path), str(temp_dir / "slide")],
        capture_output=True, text=True, check=True,
    )

    return sorted(temp_dir.glob("slide-*.jpg"))


def make_hidden_placeholder(size: tuple[int, int]) -> Image.Image:
    """Create a crosshatch placeholder for hidden slides."""
    img = Image.new("RGB", size, color="#F0F0F0")
    draw = ImageDraw.Draw(img)
    lw = max(5, min(size) // 100)
    draw.line([(0, 0), size], fill="#CCCCCC", width=lw)
    draw.line([(size[0], 0), (0, size[1])], fill="#CCCCCC", width=lw)
    return img


def build_slide_list(
    slide_info: list[dict],
    visible_images: list[Path],
    temp_dir: Path,
) -> list[tuple[Path, str]]:
    """Match slide metadata with rendered images, creating placeholders for hidden slides."""
    if visible_images:
        with Image.open(visible_images[0]) as img:
            ph_size = img.size
    else:
        ph_size = (1920, 1080)

    slides = []
    vis_idx = 0
    for info in slide_info:
        if info["hidden"]:
            ph_path = temp_dir / f"hidden-{info['name']}.jpg"
            make_hidden_placeholder(ph_size).save(ph_path, "JPEG")
            slides.append((ph_path, f"{info['name']} (hidden)"))
        else:
            if vis_idx < len(visible_images):
                slides.append((visible_images[vis_idx], info["name"]))
                vis_idx += 1

    return slides


def create_grid(
    slides: list[tuple[Path, str]],
    cols: int,
    width: int,
) -> Image.Image:
    """Create a single grid image from slide thumbnails."""
    font_size = int(width * FONT_RATIO)
    label_pad = int(font_size * LABEL_PAD_RATIO)

    with Image.open(slides[0][0]) as img:
        aspect = img.height / img.width
    height = int(width * aspect)

    rows = (len(slides) + cols - 1) // cols
    cell_h = height + font_size + label_pad * 2
    grid_w = cols * width + (cols + 1) * PADDING
    grid_h = rows * cell_h + (rows + 1) * PADDING

    grid = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.load_default(size=font_size)
    except Exception:
        font = ImageFont.load_default()

    for i, (img_path, label) in enumerate(slides):
        row, col = i // cols, i % cols
        x = col * width + (col + 1) * PADDING
        y_base = row * cell_h + (row + 1) * PADDING

        # Label
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text((x + (width - text_w) // 2, y_base + label_pad), label, fill="black", font=font)

        # Thumbnail
        y_thumb = y_base + label_pad + font_size + label_pad
        with Image.open(img_path) as img:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            w, h = img.size
            tx = x + (width - w) // 2
            ty = y_thumb + (height - h) // 2
            grid.paste(img, (tx, ty))
            if BORDER > 0:
                draw.rectangle(
                    [(tx - BORDER, ty - BORDER), (tx + w + BORDER - 1, ty + h + BORDER - 1)],
                    outline="gray", width=BORDER,
                )

    return grid


def create_grids(
    slides: list[tuple[Path, str]],
    cols: int,
    width: int,
    output_path: Path,
) -> list[str]:
    """Create one or more grid images (max 12 slides per grid)."""
    max_per = cols * (cols + 1)
    files = []

    for chunk_i, start in enumerate(range(0, len(slides), max_per)):
        chunk = slides[start:start + max_per]
        grid = create_grid(chunk, cols, width)

        if len(slides) <= max_per:
            out = output_path
        else:
            out = output_path.parent / f"{output_path.stem}-{chunk_i + 1}{output_path.suffix}"

        out.parent.mkdir(parents=True, exist_ok=True)
        grid.save(str(out), quality=JPEG_QUALITY)
        files.append(str(out))

    return files


def export_per_slide(
    slides: list[tuple[Path, str]],
    output_dir: Path,
) -> list[str]:
    """Write one JPEG per slide with slide index and XML name in the filename."""
    output_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for i, (img_path, label) in enumerate(slides, start=1):
        safe = label.replace(".xml", "").replace(" ", "_").replace("/", "-")
        out = output_dir / f"slide{i:02d}-{safe}.jpg"
        with Image.open(img_path) as img:
            img.save(str(out), "JPEG", quality=JPEG_QUALITY)
        files.append(str(out))
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Create PPTX thumbnail grid and/or per-slide JPEGs for layout QA",
    )
    parser.add_argument("input", help="Input .pptx file")
    parser.add_argument("output_prefix", nargs="?", default="thumbnails",
                        help="Output prefix for grid JPG (default: thumbnails)")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS,
                        help=f"Grid columns (default: {DEFAULT_COLS}, max: {MAX_COLS})")
    parser.add_argument("--dpi", type=int, default=DPI,
                        help=f"PDF/JPEG resolution (default: {DPI}; use 150 for layout detail)")
    parser.add_argument("--per-slide", type=Path, metavar="DIR",
                        help="Export one JPEG per slide into DIR (slide01-slide1.xml.jpg, ...)")
    parser.add_argument("--no-grid", action="store_true",
                        help="Skip thumbnail grid (use with --per-slide only)")
    args = parser.parse_args()

    if args.no_grid and not args.per_slide:
        print("Error: --no-grid requires --per-slide", file=sys.stderr)
        sys.exit(1)

    cols = min(args.cols, MAX_COLS)
    input_path = Path(args.input)

    if not input_path.exists() or input_path.suffix.lower() != ".pptx":
        print(f"Error: Invalid PowerPoint file: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(f"{args.output_prefix}.jpg")
    slide_info = get_slide_info(input_path)

    with tempfile.TemporaryDirectory() as td:
        temp = Path(td)
        images = convert_to_images(input_path, temp, dpi=args.dpi)
        slides = build_slide_list(slide_info, images, temp)

        if args.per_slide:
            slide_files = export_per_slide(slides, args.per_slide)
            print(f"Exported {len(slide_files)} slide image(s) to {args.per_slide}:")
            for sf in slide_files:
                print(f"  {sf}")

        if not args.no_grid:
            grid_files = create_grids(slides, cols, THUMB_WIDTH, output_path)
            print(f"Created {len(grid_files)} grid(s):")
            for gf in grid_files:
                print(f"  {gf}")


if __name__ == "__main__":
    main()
