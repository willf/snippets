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
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for <title> tag
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                return title_match.group(1).strip()
            # Look for <h1> tag as fallback
            h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
            if h1_match:
                return h1_match.group(1).strip()
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
    
    # Return filename without extension as fallback
    return Path(filepath).stem.replace('_', ' ').title()


def extract_description_from_html(filepath):
    """
    Extract a description from an HTML file.
    
    Args:
        filepath: Path to the HTML file
        
    Returns:
        A description string, or empty string if none found
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Look for meta description
            meta_match = re.search(
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\'][^>]*>',
                content,
                re.IGNORECASE
            )
            if meta_match:
                return meta_match.group(1).strip()
            # Look for first paragraph as fallback
            p_match = re.search(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
            if p_match:
                desc = re.sub(r'<[^>]+>', '', p_match.group(1))  # Strip HTML tags
                desc = ' '.join(desc.split())  # Normalize whitespace
                if len(desc) > 150:
                    desc = desc[:150] + '...'
                return desc
    except Exception as e:
        print(f"Warning: Could not read {filepath}: {e}")
    
    return ""


def find_html_snippets(directory='.'):
    """
    Find all HTML files in the directory (excluding index.html).
    
    Args:
        directory: Directory to search in (default: current directory)
        
    Returns:
        List of tuples: (filename, title, description)
    """
    snippets = []
    
    for filename in sorted(os.listdir(directory)):
        if filename.endswith('.html') and filename != 'index.html':
            filepath = os.path.join(directory, filename)
            if os.path.isfile(filepath):
                title = extract_title_from_html(filepath)
                description = extract_description_from_html(filepath)
                snippets.append((filename, title, description))
    
    return snippets


def generate_index_html(snippets, output_file='index.html'):
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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 40px 30px;
        }}
        
        .snippet-count {{
            color: #666;
            font-size: 0.95em;
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .snippets-list {{
            list-style: none;
        }}
        
        .snippet-item {{
            background: #f8f9fa;
            border-radius: 8px;
            margin-bottom: 20px;
            padding: 25px;
            transition: all 0.3s ease;
            border-left: 4px solid #667eea;
        }}
        
        .snippet-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            background: #f1f3f5;
        }}
        
        .snippet-item h2 {{
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #2d3748;
        }}
        
        .snippet-item h2 a {{
            color: #667eea;
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .snippet-item h2 a:hover {{
            color: #764ba2;
        }}
        
        .snippet-description {{
            color: #666;
            margin-bottom: 12px;
            line-height: 1.5;
        }}
        
        .snippet-filename {{
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            color: #999;
            background: #e9ecef;
            padding: 4px 8px;
            border-radius: 4px;
            display: inline-block;
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
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}
        
        footer a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        footer a:hover {{
            text-decoration: underline;
        }}
        
        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 30px 20px;
            }}
            
            .snippet-item {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Code Snippets</h1>
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
        snippet_count = f"Found {len(snippets)} snippet{'s' if len(snippets) != 1 else ''}"
        snippets_html = '<ul class="snippets-list">\n'
        
        for filename, title, description in snippets:
            snippets_html += f'                <li class="snippet-item">\n'
            snippets_html += f'                    <h2><a href="{filename}">{title}</a></h2>\n'
            if description:
                snippets_html += f'                    <p class="snippet-description">{description}</p>\n'
            snippets_html += f'                    <span class="snippet-filename">{filename}</span>\n'
            snippets_html += f'                </li>\n'
        
        snippets_html += '            </ul>'
    else:
        snippet_count = "No snippets found"
        snippets_html = '''            <div class="empty-state">
                <h2>No Snippets Yet</h2>
                <p>Add HTML files to this directory and run generate.py again.</p>
            </div>'''
    
    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Fill in the template
    html_content = html_template.format(
        snippet_count=snippet_count,
        snippets_content=snippets_html,
        timestamp=timestamp
    )
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
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


if __name__ == '__main__':
    main()
