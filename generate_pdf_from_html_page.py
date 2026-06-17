# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright",
# ]
# ///

import argparse
import subprocess
import sys
from playwright.sync_api import sync_playwright


def ensure_browsers_installed():
    """Ensure the Playwright Chromium binary is installed."""
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print("Warning: Could not automatically verify Playwright browsers.")


def fetch_interlinear_pdf(
    url: str, output_path: str, render_scale: float, margin_size: str
):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        print(f"Loading {url}...")
        page.goto(url, wait_until="networkidle")

        # --- THE FIX: Inject custom CSS ---
        # 1. Hides the BibleHub top navigation and footers
        # 2. Prevents the interlinear groupings from snapping in half across pages
        page.add_style_tag(
            content="""
            .topbg, #topheading, nav, header, footer { display: none !important; }
            .int-struct, tr, td, table { page-break-inside: avoid !important; }
            body { padding-top: 10px !important; }
        """
        )

        page.emulate_media(media="screen")

        print(f"Saving PDF to {output_path}...")

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            scale=render_scale,
            margin={
                "top": margin_size,
                "bottom": margin_size,
                "left": margin_size,
                "right": margin_size,
            },
        )

        browser.close()
        print(f"Done! Saved as {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert an interlinear webpage to a cleanly formatted PDF."
    )
    parser.add_argument("url", help="The URL of the webpage.")
    parser.add_argument(
        "-o",
        "--output",
        default="output.pdf",
        help="Saved PDF filename (default: output.pdf)",
    )
    parser.add_argument(
        "-s",
        "--scale",
        type=float,
        default=1.0,
        help="Scale the rendering (default: 1.0)",
    )

    # New argument to control margins
    parser.add_argument(
        "-m", "--margin", default="0.3in", help="Margin size (default: 0.3in)"
    )

    args = parser.parse_args()

    print("Checking for browser binaries...")
    ensure_browsers_installed()

    fetch_interlinear_pdf(args.url, args.output, args.scale, args.margin)
