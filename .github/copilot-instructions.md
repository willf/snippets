# Copilot Instructions

## Build, test, and lint commands

This repository is managed as a small `uv`-based Python workspace rather than a packaged application.

- Install dependencies: `uv sync`
- Run the documented HTML index generator: `uv run python generate.py`
- Run a script directly: `uv run python <script>.py`
- Alternative without `uv`: `python3 <script>.py`

There is no configured automated test suite, no lint configuration, and no CI workflow in this repository right now. There are also no single-test commands because no test runner is set up.

When you need to validate a change, prefer running the specific script you edited with realistic local inputs instead of inventing new tooling.

## High-level architecture

The repository has two main shapes of work that share the same root directory.

First, it contains static one-page HTML snippets such as `decade.html`, `distributions.html`, `dow.html`, `poem_matrix.html`, and `kpl_modal.html`. `generate.py` scans the repository root for `*.html` files except `index.html`, extracts a title and description from each file, and regenerates `index.html` as an index page. `README.md` describes this workflow, and `index.html` should be treated as generated output.

Second, it contains a collection of standalone Python utilities for domain-specific data work. These scripts are not wired together as a single application; they are run ad hoc against local files, SQLite data, or remote sources:

- Sacred Harp / minutes data:
  - `scrape_fasola_minutes.py` scrapes minute pages and writes CSV summaries.
  - `sqlite_to_jsonl.py` exports rows from `minutes.db` to `names.jsonl`.
  - `find_dupes.py` reads JSONL from stdin, performs fuzzy duplicate clustering, and writes CSV to stdout.
  - `get_songs_by_leader.py` queries `minutes.db` for leader/song relationships.
- Text/document conversion:
  - `lyrics_to_json.py` merges TSV metadata with per-song text files into JSONL.
  - `combine_docs.py` combines sequential Markdown files and adds page markers.
  - `semantic_diff.py` compares JSON or JSONL files semantically rather than textually.
- Other one-off generators and utilities:
  - `dcp_2025.py` generates liturgical reading Markdown from local/remote JSON plus Bible API fetches.
  - `ytplaylist_to_md.py` turns a playlist into tab-separated Markdown-like output.
  - `upload_hf_images.py` uploads an image folder as a Hugging Face dataset.

Important local artifacts such as `minutes.db`, `2025_edition.jsonl`, `names.jsonl`, `dupes.csv`, `cluster_similarity_results.csv`, and generated HTML/PDF files live in the repository root alongside the scripts. Changes often need to preserve these file-based workflows instead of introducing package structure or abstractions that do not match the repo.

## Key conventions

- Most code is root-level, single-purpose Python scripts with `if __name__ == "__main__":` entry points. Prefer extending an existing script over introducing a framework or a new package layout.
- Scripts commonly use `argparse` for CLI behavior, and several are designed for shell pipelines. For example, `find_dupes.py` consumes JSONL from stdin and writes CSV to stdout, while `lyrics_to_json.py` can write either to a file or stdout.
- JSONL is a recurring interchange format across the repo. When adding new data-processing steps, prefer stream-friendly JSONL/CSV workflows over large in-memory transformations.
- Local files and generated outputs are part of the normal workflow. Be careful not to treat files like `index.html`, CSV exports, or derived JSONL files as hand-maintained unless the script pattern indicates otherwise.
- `generate.py` relies on lightweight HTML metadata conventions: it prefers a `<title>`, falls back to `<h1>`, then falls back to the filename; descriptions come from a meta description tag or the first paragraph. Preserve that behavior if you change snippet discovery.
- Data-processing scripts favor small helper functions plus procedural `main()` logic instead of classes. Match that style unless there is a strong reason to refactor broadly.
- Several scripts encode configuration as uppercase module-level constants near the top of the file, especially for URLs, output paths, and other run-specific settings. Keep new configuration consistent with that pattern when editing those utilities.
- This repo does not currently define shared lint/test expectations in config files. Do not claim nonexistent checks in generated instructions or automation.
