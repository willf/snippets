# Snippets

A place to share snippets of code and small one-page apps, by Will Fitzgerald.

See also: [Snippets](https://willf.github.io/snippets/) on GitHub pages.

## Structure

- **`index.html`** - Auto-generated index page that lists all available snippets
- **`generate.py`** - Python script to generate index.html from HTML files in the directory
- **`python_scripts.yaml`** - Metadata and visibility settings for the Python scripts listed on the index
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

### Listing Python Scripts

Python utilities are listed separately using `python_scripts.yaml`. Add each script's filename, description, and `show_on_index` setting there. The generated index links each visible script to its source on GitHub.

### Tips for Creating Snippets

- Include a `<title>` tag in your HTML for a proper title in the index
- Add a meta description or a first paragraph for a snippet description
- Include a link back to `index.html` for easy navigation
