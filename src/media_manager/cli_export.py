"""CLI for image export — resize and convert images."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _emit_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _error_json(message: str) -> dict:
    return {"status": "error", "message": message}


def cmd_export(args: argparse.Namespace) -> int:
    source = Path(args.source)
    target = Path(args.target)
    width = args.width
    quality = args.quality
    format_name = args.format

    if not source.is_file():
        payload = _error_json(f"Source not found: {source}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Source not found: {source}", file=sys.stderr)
        return 1

    try:
        from PIL import Image
    except ImportError:
        payload = _error_json("Pillow (PIL) is required. Install with: pip install Pillow")
        if args.json:
            _emit_json(payload)
        else:
            print("Error: Pillow (PIL) is required. Install with: pip install Pillow", file=sys.stderr)
        return 1

    try:
        img = Image.open(source)

        if width and width > 0:
            ratio = width / img.width
            new_height = int(img.height * ratio)
        elif args.height and args.height > 0:
            ratio = args.height / img.height
            width = int(img.width * ratio)
            new_height = args.height
        else:
            width = img.width
            new_height = img.height

        img = img.resize((width, new_height), Image.LANCZOS)

        if target.suffix.lower() in (".jpg", ".jpeg"):
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(target, format_name or "JPEG", quality=quality)
        elif target.suffix.lower() == ".png":
            img.save(target, format_name or "PNG")
        elif target.suffix.lower() == ".webp":
            img.save(target, format_name or "WEBP", quality=quality)
        else:
            img.save(target, format_name or "JPEG", quality=quality)

        payload = {
            "status": "exported",
            "source": str(source),
            "target": str(target),
            "width": width,
            "height": new_height,
            "quality": quality,
        }
    except Exception as exc:
        payload = _error_json(f"Export failed: {exc}")
        if args.json:
            _emit_json(payload)
        else:
            print(f"Error: Export failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        _emit_json(payload)
    else:
        print(f"Exported: {source} -> {target} ({width}x{new_height}, quality={quality})")
    return 0


def cmd_contact_sheet(args: argparse.Namespace) -> int:
    image_paths = args.images
    if not image_paths:
        print("Error: At least one image path is required.", file=sys.stderr)
        return 1

    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Error: Pillow (PIL) is required.", file=sys.stderr)
        return 1

    width = args.width
    cols = args.cols
    rows = (len(image_paths) + cols - 1) // cols
    margin = args.margin
    spacing = args.spacing
    label_height = 24
    output_path = args.output
    title = args.title

    canvas_w = cols * width + (cols + 1) * spacing + 2 * margin
    canvas_h = rows * (width + label_height) + (rows + 1) * spacing + 2 * margin + 40

    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype("arial.ttf", 18)
    except Exception:
        font_title = ImageFont.load_default()
    try:
        font_label = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font_label = ImageFont.load_default()

    draw.text((margin, margin), title, fill="black", font=font_title)

    for idx, img_path_str in enumerate(image_paths):
        row = idx // cols
        col = idx % cols
        x = margin + col * (width + spacing)
        y = margin + 40 + row * (width + label_height + spacing)
        try:
            img = Image.open(img_path_str)
            img.thumbnail((width, width), Image.LANCZOS)
            ox = x + (width - img.width) // 2
            oy = y + (width - img.height) // 2
            canvas.paste(img, (ox, oy))
        except Exception:
            draw.rectangle([x, y, x + width, y + width], outline="gray")
            draw.text((x + 5, y + width // 2 - 10), "Error", fill="red", font=font_label)

        name = Path(img_path_str).name
        if len(name) > 20:
            name = name[:17] + "..."
        draw.text((x, y + width + 2), name, fill="black", font=font_label)

    canvas.save(output_path, "PDF", resolution=150)

    payload = {
        "status": "created",
        "output": str(output_path),
        "images": len(image_paths),
        "cols": cols,
        "rows": rows,
    }
    if args.json:
        _emit_json(payload)
    else:
        print(f"Contact sheet: {output_path} ({len(image_paths)} images, {cols}x{rows})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="media-manager export",
        description="Export images — resize, convert, and generate contact sheets.",
        epilog=(
            "Examples:\n"
            "  media-manager export image --source photo.jpg --target resized.jpg --width 1920 --quality 85\n"
            "  media-manager export image --source photo.png --target out.jpg --width 1024 --json\n"
            "  media-manager export contact-sheet --images *.jpg --output sheet.pdf --title \"Trip 2024\"\n"
            "  media-manager export contact-sheet --images *.jpg --output sheet.pdf --cols 5 --width 300\n"
        ),
    )
    subparsers = parser.add_subparsers(dest="export_action")

    image_p = subparsers.add_parser("image", help="Resize and export a single image.")
    image_p.add_argument("--source", type=Path, required=True, help="Source image path.")
    image_p.add_argument("--target", type=Path, required=True, help="Target output path.")
    image_p.add_argument("--width", type=int, default=2048, help="Target width in pixels (default: 2048).")
    image_p.add_argument("--height", type=int, default=0, help="Target height in pixels. Overrides width-based scaling when set.")
    image_p.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality 1-100 (default: 85).")
    image_p.add_argument("--format", choices=["JPEG", "PNG", "WEBP"], help="Output format override.")
    image_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    contact_p = subparsers.add_parser("contact-sheet", help="Generate a contact sheet PDF from images.")
    contact_p.add_argument("--images", nargs="+", required=True, help="One or more image paths.")
    contact_p.add_argument("--output", type=Path, required=True, help="Output PDF path.")
    contact_p.add_argument("--title", default="Contact Sheet", help="Title for the contact sheet.")
    contact_p.add_argument("--cols", type=int, default=4, help="Number of columns (default: 4).")
    contact_p.add_argument("--width", type=int, default=200, help="Thumbnail size in pixels (default: 200).")
    contact_p.add_argument("--margin", type=int, default=20, help="Page margin in pixels (default: 20).")
    contact_p.add_argument("--spacing", type=int, default=10, help="Spacing between thumbnails (default: 10).")
    contact_p.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    return parser


ACTION_HANDLERS = {
    "image": cmd_export,
    "contact-sheet": cmd_contact_sheet,
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.export_action is None:
        parser.print_help()
        return 0

    handler = ACTION_HANDLERS.get(args.export_action)
    if handler is None:
        print(f"Unknown export action: {args.export_action}", file=sys.stderr)
        return 1

    return handler(args)
