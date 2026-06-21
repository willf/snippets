#!/usr/bin/env python3
"""Configure SBL Greek as a self-hosted web font in an HTML file.

What this script does:
1. Optionally copies a provided SBL font file into a local fonts directory.
2. Detects available SBL web font files (.woff2/.woff/.ttf).
3. Injects (or updates) an @font-face block in the target HTML <style> section.

Usage examples:
  uv run python configure_sbl_greek_font.py \
    --html gregory-nyssa-beatitudes-sermon-1.html \
    --fonts-dir fonts \
    --font-base SBL_grk

  uv run python configure_sbl_greek_font.py \
    --html gregory-nyssa-beatitudes-sermon-1.html \
    --fonts-dir fonts \
    --font-source ~/Downloads/SBL_grk.ttf \
    --font-base SBL_grk
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

START_MARKER = "/* SBL Greek webfont: start */"
END_MARKER = "/* SBL Greek webfont: end */"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", required=True, help="Path to target HTML file")
    parser.add_argument(
        "--fonts-dir",
        default="fonts",
        help="Directory (relative to HTML) where font files are hosted",
    )
    parser.add_argument(
        "--font-base",
        default="SBL_grk",
        help="Base filename for font files, e.g. SBL_grk for SBL_grk.woff2",
    )
    parser.add_argument(
        "--font-family",
        default="SBL Greek",
        help="CSS font-family name to register via @font-face",
    )
    parser.add_argument(
        "--font-source",
        help="Optional path to a local .ttf/.woff/.woff2 file to copy into --fonts-dir",
    )
    return parser.parse_args()


def maybe_copy_font(font_source: str | None, fonts_dir: Path) -> None:
    if not font_source:
        return

    src = Path(font_source).expanduser().resolve()
    if not src.exists() or not src.is_file():
        raise FileNotFoundError(f"Font source not found: {src}")

    if src.suffix.lower() not in {".ttf", ".woff", ".woff2"}:
        raise ValueError("--font-source must end with .ttf, .woff, or .woff2")

    fonts_dir.mkdir(parents=True, exist_ok=True)
    dst = fonts_dir / src.name
    shutil.copy2(src, dst)
    print(f"Copied font file: {dst}")


def build_src_list(fonts_dir_rel: str, font_base: str, html_parent: Path) -> list[str]:
    entries: list[tuple[str, str]] = [
        (".woff2", "woff2"),
        (".woff", "woff"),
        (".ttf", "truetype"),
    ]

    src_lines: list[str] = []
    for ext, fmt in entries:
        candidate = html_parent / fonts_dir_rel / f"{font_base}{ext}"
        if candidate.exists():
            url = f"{fonts_dir_rel}/{font_base}{ext}".replace("\\", "/")
            src_lines.append(f'url("{url}") format("{fmt}")')

    return src_lines


def make_fontface_block(font_family: str, src_lines: list[str]) -> str:
    joined = ",\n         ".join(src_lines)
    return (
        f"{START_MARKER}\n"
        "@font-face {\n"
        f'  font-family: "{font_family}";\n'
        f"  src: {joined};\n"
        "  font-style: normal;\n"
        "  font-weight: 400;\n"
        "  font-display: swap;\n"
        "}\n"
        f"{END_MARKER}"
    )


def replace_or_insert_block(style_text: str, new_block: str) -> str:
    if START_MARKER in style_text and END_MARKER in style_text:
        start = style_text.index(START_MARKER)
        end = style_text.index(END_MARKER) + len(END_MARKER)
        return style_text[:start] + new_block + style_text[end:]

    return new_block + "\n\n" + style_text


def update_html(html_path: Path, font_family: str, src_lines: list[str]) -> None:
    text = html_path.read_text(encoding="utf-8")

    style_open = text.find("<style>")
    style_close = text.find("</style>")
    if style_open == -1 or style_close == -1 or style_close <= style_open:
        raise RuntimeError("Could not find a valid <style>...</style> block in HTML")

    css_start = style_open + len("<style>")
    css = text[css_start:style_close]

    block = make_fontface_block(font_family, src_lines)
    updated_css = replace_or_insert_block(css.lstrip("\n"), block)

    updated = text[:css_start] + "\n" + updated_css.rstrip() + "\n    " + text[style_close:]
    html_path.write_text(updated, encoding="utf-8")


def main() -> int:
    args = parse_args()

    html_path = Path(args.html).expanduser().resolve()
    if not html_path.exists():
        print(f"HTML file not found: {html_path}", file=sys.stderr)
        return 1

    html_parent = html_path.parent
    fonts_dir = (html_parent / args.fonts_dir).resolve()

    try:
        maybe_copy_font(args.font_source, fonts_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    src_lines = build_src_list(args.fonts_dir, args.font_base, html_parent)
    if not src_lines:
        print(
            "No font files found. Add one or more of: "
            f"{args.fonts_dir}/{args.font_base}.woff2, "
            f"{args.fonts_dir}/{args.font_base}.woff, "
            f"{args.fonts_dir}/{args.font_base}.ttf",
            file=sys.stderr,
        )
        return 1

    try:
        update_html(html_path, args.font_family, src_lines)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Updated {html_path.name} with @font-face for '{args.font_family}'.")
    print("Detected sources:")
    for line in src_lines:
        print(f"  - {line}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
