import sqlite3
import argparse
import re
import csv
import sys


def get_songs_by_leader(leader_name, db_path="minutes.db"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = """
        SELECT DISTINCT
            songs.title,
            book_song_joins.page_num
        FROM song_leader_joins
        JOIN leaders ON song_leader_joins.leader_id = leaders.id
        JOIN songs ON song_leader_joins.song_id = songs.id
        JOIN book_song_joins ON songs.id = book_song_joins.song_id
        JOIN books ON book_song_joins.book_id = books.id
        WHERE leaders.name = ?;
        """

        cursor.execute(query, (leader_name,))
        rows = cursor.fetchall()

        if not rows:
            print(f"No songs found for leader: {leader_name}")
            return

        def calculate_sort_key(page_num):
            val = 0.0
            if page_num:
                match = re.search(r"(\d+)([tb]?)", str(page_num))
                if match:
                    val = float(match.group(1))
                    suffix = match.group(2)
                    if suffix == "t":
                        val += 0.1
                    elif suffix == "b":
                        val += 0.2
            return val

        # Transform rows to include sort key
        processed_rows = []
        for row in rows:
            song_title, page_num = row
            sort_val = calculate_sort_key(page_num)
            processed_rows.append((song_title, page_num, sort_val))

        processed_rows.sort(key=lambda x: (x[2]))

        writer = csv.writer(sys.stdout)
        writer.writerow(["Song", "Page", "Numeric Key"])

        for row in processed_rows:
            writer.writerow(row)

        conn.close()

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get songs led by a specific leader.")
    parser.add_argument(
        "leader", nargs="?", default="Will Fitzgerald", help="Name of the leader"
    )
    parser.add_argument("--db", default="minutes.db", help="Path to sqlite database")

    args = parser.parse_args()

    get_songs_by_leader(args.leader, args.db)
