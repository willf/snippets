import sqlite3
import json
import sys

def export_jsonl(db_path, query, output_file):
    # 1. Connect to the database
    conn = sqlite3.connect(db_path)

    # 2. Key Step: Set row_factory to sqlite3.Row
    # This allows us to convert rows to dictionaries (key-value pairs)
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()
    cursor.execute(query)

    # 3. Stream results to file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Iterating the cursor fetches rows one by one (generator)
        # instead of loading all 22k+ rows into RAM at once.
        for row in cursor:
            # Convert the SQLite Row object to a standard Python dict
            row_dict = dict(row)

            # Dump to JSON and write with a newline
            f.write(json.dumps(row_dict) + '\n')

    conn.close()
    print(f"Successfully exported query to {output_file}")

if __name__ == "__main__":
    # Configuration
    DATABASE = 'minutes.db'
    QUERY = "SELECT * FROM leaders"
    OUTPUT = 'names.jsonl'

    export_jsonl(DATABASE, QUERY, OUTPUT)
