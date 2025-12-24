# Snippets

A place to share snippets of code and small one-page apps.

## Structure

- **`index.html`** - Auto-generated index page that lists all available snippets
- **`generate.py`** - Python script to generate index.html from HTML files in the directory
- **`kpl_modal.html`** - Example modal dialog snippet

## Usage

### Viewing Snippets

Open `index.html` in your browser to see the list of all available snippets. Click on any snippet to view it.

### Adding New Snippets

1. Add your HTML file to the root directory (e.g., `my_snippet.html`)
2. Run the generator script:
   ```bash
   python3 generate.py
   ```
3. The index.html will be automatically updated with your new snippet

### Tips for Creating Snippets

- Include a `<title>` tag in your HTML for a proper title in the index
- Add a meta description or a first paragraph for a snippet description
- Include a link back to `index.html` for easy navigation
