import sqlite3
import csv
import itertools
from collections import defaultdict
import os

# --- CONFIGURATION ---
DB_PATH = 'minutes.db'      # Path to your SQLite DB
INPUT_CSV = 'dupes.csv'        # Path to your input CSV file
OUTPUT_CSV = 'cluster_similarity_results.csv' # Path for the output report
CSV_DELIMITER = ','              # Use ',' for comma, '\t' for tab-separated (based on your snippet)

def load_clusters(csv_path, delimiter):
    """
    Reads the CSV file and groups leader IDs by their Cluster_ID.
    Returns: { '1': [id1, id2], '2': [id3, id4] }
    """
    print(f"--- Loading clusters from {csv_path} ---")
    cluster_groups = defaultdict(list)
    leader_names = {} # Helper to store names for the output

    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=delimiter)

            # Strip whitespace from headers just in case
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

            for row in reader:
                try:
                    c_id = row['Cluster_ID']
                    l_id = int(row['id'])
                    name = row['name']

                    cluster_groups[c_id].append(l_id)
                    leader_names[l_id] = name
                except (ValueError, KeyError) as e:
                    print(f"Skipping invalid row: {row} ({e})")

    except FileNotFoundError:
        print(f"Error: Could not find file {csv_path}")
        return {}, {}

    print(f"Found {len(cluster_groups)} clusters.")
    return cluster_groups, leader_names

def build_social_graph(db_path):
    """
    Connects to DB and builds a map of who sings with whom.
    Returns: { leader_id: set(all_co_leaders) }
    """
    print("--- Building social graph from database ---")

    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return {}

    # 1. Fetch raw joins (Who led at which minutes?)
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # We only need minutes_id and leader_id to determine co-presence
        cursor.execute("SELECT minutes_id, leader_id FROM song_leader_joins")
        rows = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {}

    # 2. Group leaders by the minutes (event) they attended
    # minutes_attendees: { minutes_id: [leader_id, leader_id, ...] }
    minutes_attendees = defaultdict(list)
    for minutes_id, leader_id in rows:
        minutes_attendees[minutes_id].append(leader_id)

    # 3. Build the 'Social Set' for each leader
    # leader_connections: { leader_id: set(all_people_they_met) }
    leader_connections = defaultdict(set)

    # Iterate through every event
    for attendees in minutes_attendees.values():
        attendee_set = set(attendees) # Convert to set for O(1) lookups

        for person in attendees:
            # Add everyone else at this singing to this person's set
            # The union operation handles duplicates automatically
            leader_connections[person].update(attendee_set)

    # Remove the leaders themselves from their own sets
    for person, friends in leader_connections.items():
        friends.discard(person)

    print(f"Social graph built for {len(leader_connections)} leaders.")
    return leader_connections

def calculate_jaccard_index(set_a, set_b):
    """
    Returns Jaccard Similarity: (Intersection / Union)
    """
    if not set_a or not set_b:
        return 0.0, 0, 0

    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))

    if union == 0:
        return 0.0, 0, 0

    return (intersection / union), intersection, union

def main():
    # 1. Load the Clusters
    clusters, leader_names = load_clusters(INPUT_CSV, CSV_DELIMITER)
    if not clusters:
        return

    # 2. Build the Social Graph (Heavy lifting)
    social_graph = build_social_graph(DB_PATH)
    if not social_graph:
        return

    # 3. Perform Comparisons & Write Output
    print(f"--- Calculating similarities and writing to {OUTPUT_CSV} ---")

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Cluster_ID',
            'Leader_A_ID', 'Leader_A_Name',
            'Leader_B_ID', 'Leader_B_Name',
            'Similarity_Score', 'Shared_Connections', 'Total_Unique_Connections'
        ])

        # Iterate through each cluster
        for c_id, members in clusters.items():
            # Skip clusters with only 1 member (no pairs to compare)
            if len(members) < 2:
                continue

            # Create all unique pairs within the cluster
            # (A, B) but not (B, A)
            for id_a, id_b in itertools.combinations(members, 2):

                # Get their social sets
                set_a = social_graph.get(id_a, set())
                set_b = social_graph.get(id_b, set())

                # Calculate metrics
                score, shared, total = calculate_jaccard_index(set_a, set_b)

                # Write row
                writer.writerow([
                    c_id,
                    id_a, leader_names.get(id_a, "Unknown"),
                    id_b, leader_names.get(id_b, "Unknown"),
                    f"{score:.4f}",
                    shared,
                    total
                ])

    print("Done.")

if __name__ == "__main__":
    main()
