#!/usr/bin/env python3
"""
Generate index.html from HTML snippets in the current directory.

This script scans for HTML files (excluding index.html itself) and creates
an index page listing all available snippets.
"""

import os
import re
from datetime import datetime
from pathlib import Path


def extract_title_from_html(filepath):
    """
    Extract the title from an HTML file.

    Args:
        filepath: Path to the HTML file

    Returns:
        The title string, or the filename if no title is found
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Look for <title> tag
            title_match = re.search(
                r"<title>(.*?)</title>", content, re.IGNORECASE | re.DOTALL
            )
            if title_match:
                return title_match.group(1).strip()
            # Look for <h1> tag as fallback
            h1_match = re.search(
                r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL
            )
            if h1_match:
                return h1_match.group(1).strip()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")

    # Return filename without extension as fallback
    return Path(filepath).stem.replace("_", " ").title()


def extract_description_from_html(filepath):
    """
    Extract a description from an HTML file.

    Args:
        filepath: Path to the HTML file

    Returns:
        A description string, or empty string if none found
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            # Look for meta description
            meta_match = re.search(
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
                content,
                re.IGNORECASE,
            )
            if meta_match:
                return meta_match.group(1).strip()
            # Look for first paragraph as fallback
            p_match = re.search(
                r"<p[^>]*>(.*?)</p>", content, re.IGNORECASE | re.DOTALL
            )
            if p_match:
                desc = re.sub(r"<[^>]+>", "", p_match.group(1))  # Strip HTML tags
                desc = " ".join(desc.split())  # Normalize whitespace
                if len(desc) > 150:
                    desc = desc[:150] + "..."
                return desc
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")

    return ""


def find_html_snippets(directory="."):
    """
    Find all HTML files in the directory (excluding index.html).

    Args:
        directory: Directory to search in (default: current directory)

    Returns:
        List of tuples: (filename, title, description)
    """
    snippets = []

    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".html") and filename != "index.html":
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                title = extract_title_from_html(filepath)
                description = extract_description_from_html(filepath)
                snippets.append((filename, title, description))

    return snippets


def generate_index_html(snippets, output_file="index.html"):
    """
    Generate the index.html file from the list of snippets.

    Args:
        snippets: List of tuples (filename, title, description)
        output_file: Output filename (default: index.html)
    """
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="A collection of code snippets and small one-page apps">
    <title>Code Snippets Collection</title>
    <style>
        :root {{
            --paper: #f4f0e8;
            --surface: #fffdf8;
            --ink: #202321;
            --muted: #6d706b;
            --line: #d8d2c7;
            --orange: #e86f3d;
            --teal: #2f7770;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Avenir Next', Avenir, 'Helvetica Neue', sans-serif;
            line-height: 1.5;
            color: var(--ink);
            background-color: var(--paper);
            background-image: linear-gradient(rgba(32, 35, 33, 0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(32, 35, 33, 0.035) 1px, transparent 1px);
            background-size: 28px 28px;
            min-height: 100vh;
            padding: 48px 24px;
        }}

        .container {{
            max-width: 1080px;
            margin: 0 auto;
            background: var(--surface);
            border: 1px solid var(--line);
            box-shadow: 10px 10px 0 rgba(32, 35, 33, 0.08);
            overflow: hidden;
        }}

        header {{
            background: var(--ink);
            color: var(--surface);
            padding: 56px 64px 52px;
            position: relative;
        }}

        header::after {{
            background: var(--orange);
            content: '';
            height: 8px;
            position: absolute;
            right: 0;
            top: 0;
            width: 34%;
        }}

        header h1 {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: clamp(2.6rem, 7vw, 5.6rem);
            letter-spacing: -0.04em;
            line-height: 0.95;
            margin-bottom: 18px;
            max-width: 700px;
        }}

        header p {{
            color: #c9cec8;
            font-size: 1rem;
            max-width: 420px;
        }}

        .eyebrow {{
            color: #f2a17d;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            margin-bottom: 24px;
            text-transform: uppercase;
        }}

        .content {{
            padding: 38px 64px 52px;
        }}

        .snippet-count {{
            align-items: center;
            color: var(--muted);
            display: flex;
            font-size: 0.8rem;
            font-weight: 700;
            justify-content: space-between;
            letter-spacing: 0.08em;
            margin-bottom: 22px;
            text-transform: uppercase;
        }}

        .snippets-list {{
            counter-reset: snippets;
            display: grid;
            gap: 14px;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            list-style: none;
        }}

        .snippet-item {{
            background: var(--surface);
            border: 1px solid var(--line);
            counter-increment: snippets;
            min-height: 190px;
            padding: 24px 24px 20px;
            position: relative;
            transition: background 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
        }}

        .snippet-item::before {{
            color: var(--orange);
            content: counter(snippets, decimal-leading-zero);
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }}

        .snippet-item:hover {{
            background: #fff8ee;
            border-color: var(--orange);
            transform: translateY(-3px);
        }}

        .snippet-item h2 {{
            font-family: Georgia, 'Times New Roman', serif;
            font-size: 1.45rem;
            font-weight: 400;
            line-height: 1.12;
            margin: 16px 0 10px;
        }}

        .snippet-item h2 a {{
            color: var(--ink);
            text-decoration: none;
        }}

        .snippet-item h2 a:hover {{
            color: var(--teal);
        }}

        .snippet-description {{
            color: var(--muted);
            font-size: 0.9rem;
            margin-bottom: 18px;
        }}

        .snippet-filename {{
            bottom: 20px;
            color: var(--teal);
            font-family: 'SFMono-Regular', Consolas, monospace;
            font-size: 0.7rem;
            left: 24px;
            overflow: hidden;
            position: absolute;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: calc(100% - 48px);
        }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #666;
        }}

        .empty-state h2 {{
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #999;
        }}

        footer {{
            border-top: 1px solid var(--line);
            color: var(--muted);
            font-size: 0.78rem;
            padding: 20px 64px;
        }}

        footer a {{
            color: var(--teal);
            text-decoration: none;
        }}

        footer a:hover {{
            text-decoration: underline;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 20px 12px;
            }}

            header {{
                padding: 42px 28px 38px;
            }}

            header h1 {{
                font-size: 3.4rem;
            }}

            .content {{
                padding: 28px 20px 36px;
            }}

            .snippets-list {{
                grid-template-columns: 1fr;
            }}

            .snippet-item {{
                min-height: 170px;
                padding: 20px;
            }}

            .snippet-filename {{
                bottom: 18px;
                left: 20px;
                width: calc(100% - 40px);
            }}

            footer {{
                padding: 18px 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="eyebrow">Will F / Small Web Experiments</div>
            <h1>Code<br>Snippets</h1>
            <p>A collection of code snippets and small one-page apps</p>
        </header>

        <div class="content">
            <div class="snippet-count">
                {snippet_count}
            </div>

            {snippets_content}
        </div>

        <footer>
            <p>Generated on {timestamp} | <a href="https://github.com/willf/snippets" target="_blank">View on GitHub</a></p>
        </footer>
    </div>
</body>
</html>
"""

    # Generate snippets HTML
    if snippets:
        snippet_count = (
            f"Found {len(snippets)} snippet{'s' if len(snippets) != 1 else ''}"
        )
        snippets_html = '<ul class="snippets-list">\n'

        for filename, title, description in snippets:
            snippets_html += f'                <li class="snippet-item">\n'
            snippets_html += (
                f'                    <h2><a href="{filename}">{title}</a></h2>\n'
            )
            if description:
                snippets_html += f'                    <p class="snippet-description">{description}</p>\n'
            snippets_html += f'                    <span class="snippet-filename">{filename}</span>\n'
            snippets_html += f"                </li>\n"

        snippets_html += "            </ul>"
    else:
        snippet_count = "No snippets found"
        snippets_html = """            <div class="empty-state">
                <h2>No Snippets Yet</h2>
                <p>Add HTML files to this directory and run generate.py again.</p>
            </div>"""

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Fill in the template
    html_content = html_template.format(
        snippet_count=snippet_count, snippets_content=snippets_html, timestamp=timestamp
    )

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Generated {output_file} with {len(snippets)} snippet(s)")


def main():
    """Main function to generate the index."""
    print("Scanning for HTML snippets...")
    snippets = find_html_snippets()

    print(f"Found {len(snippets)} snippet(s)")
    for filename, title, _ in snippets:
        print(f"  - {filename}: {title}")

    print("\nGenerating index.html...")
    generate_index_html(snippets)
    print("\nDone!")


if __name__ == "__main__":
    main()
