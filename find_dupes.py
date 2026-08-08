# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "rapidfuzz>=3.14.3",
# ]
# ///

## To use this script:
## 1. sqlite3 -noheader minutes.db \  "SELECT json_object('id', leaders.id, 'name', leaders.name, 'count', COUNT(song_leader_joins.id)) FROM leaders LEFT JOIN song_leader_joins ON song_leader_joins.leader_id = leaders.id GROUP BY leaders.id, leaders.name;" > /tmp/names.jsonl
## 2. cat /tmp/names.jsonl| uv run find_dupes.py | sort -n >/tmp/dupes.csv
## 3.

import sys
import json
import csv
import rapidfuzz


def max(a, b):
    return a if a > b else b


def get_sort_key(item):
    """
    Sorts by Last Name, then First Name.
    Item is a tuple: (original_index, record_dict)
    """
    name = item[1].get("name", "").lower().strip()
    parts = name.split()
    if parts:
        # Returns "Solheim Jim" for "Jim Solheim"
        return parts[-1] + " " + parts[0]
    return name


def last_name_first(name):
    parts = name.lower().strip().split()
    if parts:
        return parts[-1] + " " + parts[0]
    return name.lower().strip()


def solve_connected_components(num_records, edges):
    """
    Simple graph traversal to group connected records.
    Returns a dict: {record_index: cluster_id}
    """
    adj = {i: [] for i in range(num_records)}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)

    visited = set()
    cluster_map = {}
    current_cluster_id = 1

    for i in range(num_records):
        if i not in visited:
            # Start a new cluster
            stack = [i]
            visited.add(i)
            # Check if this node has any edges (is it a duplicate?)
            # If a node has no edges, it is unique.
            is_duplicate_group = len(adj[i]) > 0

            if is_duplicate_group:
                members = []
                while stack:
                    node = stack.pop()
                    members.append(node)
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            stack.append(neighbor)

                # Assign cluster ID to all members of this group
                for member in members:
                    cluster_map[member] = current_cluster_id
                current_cluster_id += 1
            else:
                # Optional: You can assign a unique ID or None for non-duplicates
                cluster_map[i] = None

    return cluster_map


def main():
    records = []

    # 1. Read JSONL from Stdin
    # We store the original index to track them later
    try:
        for line in sys.stdin:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    if "name" in data:
                        records.append(data)
                except json.JSONDecodeError:
                    continue
    except KeyboardInterrupt:
        pass

    sys.stdout.flush()  # Ensure the output is flushed immediately
    # 2. Sort for "Sorted Neighborhood" method
    # We create a list of (original_index, record) tuples
    indexed_records = list(enumerate(records))
    sys.stdout.flush()  # Ensure the output is flushed immediately
    sorted_records = sorted(indexed_records, key=get_sort_key)

    edges = []
    window_size = 15
    threshold = 90

    # 3. Find Pairs (Edges)
    n = len(sorted_records)
    for i in range(n):
        idx_a, record_a = sorted_records[i]
        name_a = record_a.get("name", "")

        for j in range(i + 1, min(i + window_size, n)):
            idx_b, record_b = sorted_records[j]
            name_b = record_b.get("name", "")

            if name_a == name_b:
                score = 100
            else:
                score_0 = rapidfuzz.fuzz.token_sort_ratio(name_a, name_b)
                score_1 = (
                    rapidfuzz.distance.JaroWinkler.normalized_similarity(name_a, name_b)
                    * 100
                )
                score_2 = (
                    rapidfuzz.distance.Levenshtein.normalized_similarity(
                        last_name_first(name_a), last_name_first(name_b)
                    )
                    * 100
                )
                score = max(score_0, score_1)
                score = max(score, score_2)

            if score >= threshold:
                edges.append((idx_a, idx_b))

    # 4. Cluster the Pairs
    cluster_map = solve_connected_components(len(records), edges)

    # Filter out None clusters

    cluster_map = {k: v for k, v in cluster_map.items() if v is not None}

    # put all of the clusters into a list of lists
    clusters = {}
    for idx, c_id in cluster_map.items():
        if c_id not in clusters:
            clusters[c_id] = []
        clusters[c_id].append(idx)

    # find the record with the highst count in each cluster and use that as the "corrected" name
    for c_id, indices in clusters.items():
        max_count = -1
        corrected_name = None
        for idx in indices:
            record = records[idx]
            count = record.get("count", 0)
            if count > max_count:
                max_count = count
                corrected_name = record.get("name", "")
        # Update all records in this cluster with the corrected name
        for idx in indices:
            records[idx]["corrected_name"] = corrected_name
            records[idx]["max_count"] = max_count
            records[idx]["count"] = records[idx].get(
                "count", 0
            )  # Ensure count is present
            records[idx]["cluster_id"] = c_id
            records[idx]["uncorrected_name"] = records[idx].get("name", "")

    fieldnames = [
        "cluster_id",
        "corrected_name",
        "uncorrected_name",
        "count",
        "max_count",
    ]
    # 5. Output CSV
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for idx, record in enumerate(records):
        # if max_count is less than 10, skip this record
        if record.get("max_count", 0) < 10:
            continue
        # dont print if the corrected name is the same as the uncorrected name
        if record.get("corrected_name", "") == record.get("uncorrected_name", ""):
            continue
        # else print it

        writer.writerow(
            {
                "cluster_id": record.get("cluster_id", ""),
                #  "name": record.get("name", ""),
                "uncorrected_name": record.get("uncorrected_name", ""),
                "corrected_name": record.get("corrected_name", ""),
                "count": record.get("count", 0),
                "max_count": record.get("max_count", 0),
            }
        )


if __name__ == "__main__":
    main()
