import csv
import json
import argparse
import sys
from pathlib import Path
from contextlib import contextmanager

@contextmanager
def smart_open(filename=None, mode='w', encoding='utf-8'):
    """
    Context manager that yields a file object if a filename is provided,
    otherwise yields sys.stdout.
    """
    if filename and filename != '-':
        fh = open(filename, mode, encoding=encoding)
        try:
            yield fh
        finally:
            fh.close()
    else:
        yield sys.stdout

def parse_lyrics_file(file_path):
    """
    Reads a lyrics file, skips the title line, and returns the verses.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        if not lines:
            return ""

        # Skip the first line (title)
        body_lines = lines[1:]

        # Rejoin and strip extra whitespace from ends
        full_text = "".join(body_lines).strip()

        return full_text
    except FileNotFoundError:
        print(f"Warning: File not found: {file_path}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return None

def main():
    parser = argparse.ArgumentParser(description="Merge Sacred Harp metadata and lyrics into JSONL.")
    parser.add_argument("metadata_file", help="Path to the metadata file (assumed TSV)")
    parser.add_argument("lyrics_dir", help="Directory containing the lyrics text files")
    parser.add_argument("--output", "-o", help="Output JSONL file name. Defaults to STDOUT if omitted.")

    args = parser.parse_args()

    metadata_path = Path(args.metadata_file)
    lyrics_dir = Path(args.lyrics_dir)

    if not metadata_path.exists():
        sys.exit(f"Error: Metadata file '{metadata_path}' not found.")
    if not lyrics_dir.exists():
        sys.exit(f"Error: Lyrics directory '{lyrics_dir}' not found.")

    records_processed = 0

    # Open the metadata file for reading
    with open(metadata_path, 'r', encoding='utf-8') as meta_f:
        # Open the output (File or STDOUT)
        with smart_open(args.output) as out_f:

            # Assuming Tab Separated (TSV) based on your example
            reader = csv.DictReader(meta_f, delimiter='\t')

            # Clean up field names (strip whitespace)
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            for row in reader:
                clean_row = {k: v.strip() for k, v in row.items()}

                # Get the page number to find the file
                page_num = clean_row.get('Sort')

                if not page_num:
                    print(f"Skipping row with missing Page number: {clean_row}", file=sys.stderr)
                    continue

                # Construct filename (e.g., "170.txt")
                txt_filename = f"{page_num}.txt"
                txt_path = lyrics_dir / txt_filename

                # Get lyrics
                lyrics_text = parse_lyrics_file(txt_path)

                if lyrics_text is not None:
                    clean_row['text'] = lyrics_text

                    # Write JSON line to output (stdout or file)
                    out_f.write(json.dumps(clean_row, ensure_ascii=False) + '\n')
                    records_processed += 1

    # Print summary to stderr so it doesn't mess up the pipeline
    print(f"Successfully processed {records_processed} records.", file=sys.stderr)

if __name__ == "__main__":
    main()
