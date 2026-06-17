import os
import re
import glob
import argparse

def int_to_roman(num):
    """Converts an integer to a lowercase Roman numeral."""
    values = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4, 1
    ]
    symbols = [
        "m", "cm", "d", "cd",
        "c", "xc", "l", "xl",
        "x", "ix", "v", "iv", "i"
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // values[i]):
            roman_num += symbols[i]
            num -= values[i]
        i += 1
    return roman_num

def parse_ranges(range_args):
    """
    Parses range arguments like '4-17:roman' into a dictionary mapping 
    the file index to its formatted page string.
    """
    page_mapping = {}
    
    if not range_args:
        return page_mapping

    for r in range_args:
        try:
            range_part, num_type = r.split(':')
            start_str, end_str = range_part.split('-')
            start = int(start_str)
            end = int(end_str)
            num_type = num_type.lower()
            
            page_counter = 1
            for i in range(start, end + 1):
                if num_type == 'roman':
                    page_str = int_to_roman(page_counter)
                elif num_type == 'arabic':
                    page_str = str(page_counter)
                else:
                    raise ValueError(f"Unknown numbering type: {num_type}. Use 'roman' or 'arabic'.")
                
                page_mapping[i] = page_str
                page_counter += 1
                
        except ValueError as e:
            print(f"Error parsing range '{r}'. Ensure format is start-end:type (e.g., 4-17:roman). Details: {e}")
            exit(1)
            
    return page_mapping

def main():
    parser = argparse.ArgumentParser(description="Combine sequential markdown files with custom page numbering.")
    parser.add_argument("-d", "--dir", required=True, help="Directory containing the markdown files.")
    parser.add_argument("-o", "--out", required=True, help="Output file path (e.g., combined.md).")
    parser.add_argument("-r", "--range", nargs='+', help="Page ranges and types. Format: start-end:type (e.g., 4-17:roman 18-271:arabic).", default=[])
    
    args = parser.parse_args()
    
    # Parse the custom numbering ranges
    page_mapping = parse_ranges(args.range)
    
    # Find and sort all markdown files in the directory
    search_pattern = os.path.join(args.dir, "*.md")
    files = sorted(glob.glob(search_pattern))
    
    if not files:
        print(f"No .md files found in directory: {args.dir}")
        return

    print(f"Found {len(files)} files. Combining into {args.out}...")

    with open(args.out, 'w', encoding='utf-8') as outfile:
        for filepath in files:
            filename = os.path.basename(filepath)
            
            # Extract the numerical part of the filename (e.g., "0004" from "document_0004.md")
            match = re.search(r'(\d+)', filename)
            if match:
                img_num_str = match.group(1)
                img_num_int = int(img_num_str)
            else:
                print(f"Warning: Could not find numbers in filename '{filename}'. Skipping.")
                continue

            # Check if this file index falls into one of our specified ranges
            page_str = page_mapping.get(img_num_int)

            # Format the header based on whether it has a defined page number
            if page_str:
                header = f"[IMAGE {img_num_str}; PAGE {page_str}]\n\n"
            else:
                header = f"[IMAGE {img_num_str}]\n\n"

            # Read the individual file and write it to the combined file
            with open(filepath, 'r', encoding='utf-8') as infile:
                content = infile.read()

            outfile.write(header)
            outfile.write(content)
            
            # Ensure there's a visual separation between files
            if not content.endswith('\n'):
                outfile.write('\n')
            outfile.write('\n---\n\n') 

    print("Done!")

if __name__ == "__main__":
    main()