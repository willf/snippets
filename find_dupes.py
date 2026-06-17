import sys
import json
import csv
import rapidfuzz

def get_sort_key(item):
    """
    Sorts by Last Name, then First Name.
    Item is a tuple: (original_index, record_dict)
    """
    name = item[1].get('name', '').lower().strip()
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
                    if 'name' in data:
                        records.append(data)
                except json.JSONDecodeError:
                    continue
    except KeyboardInterrupt:
        pass

    # 2. Sort for "Sorted Neighborhood" method
    # We create a list of (original_index, record) tuples
    indexed_records = list(enumerate(records))
    sorted_records = sorted(indexed_records, key=get_sort_key)

    edges = []
    window_size = 15
    threshold = 90

    # 3. Find Pairs (Edges)
    n = len(sorted_records)
    for i in range(n):
        idx_a, record_a = sorted_records[i]
        name_a = record_a.get('name', '')

        for j in range(i + 1, min(i + window_size, n)):
            idx_b, record_b = sorted_records[j]
            name_b = record_b.get('name', '')

            if name_a == name_b:
                score = 100
            else:
                score_0 = rapidfuzz.fuzz.token_sort_ratio(name_a, name_b)
                score_1 = rapidfuzz.distance.JaroWinkler.normalized_similarity(name_a, name_b) * 100
                score_2 = rapidfuzz.distance.Levenshtein.normalized_similarity(last_name_first(name_a), last_name_first(name_b)) * 100
                score = max(score_0, score_1, score_2)

            if score >= threshold:
                edges.append((idx_a, idx_b))

    # 4. Cluster the Pairs
    cluster_map = solve_connected_components(len(records), edges)

    # 5. Output CSV
    # We define the columns: Cluster ID, Name, and then any other fields found in the data
    fieldnames = ['Cluster_ID', 'name']

    # Add other keys from the first record just to be helpful (optional)
    if records:
        extra_keys = [k for k in records[0].keys() if k != 'name']
        fieldnames.extend(extra_keys)

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    for idx, record in enumerate(records):
        c_id = cluster_map.get(idx)

        # Only output records that are part of a duplicate cluster
        if c_id is not None:
            out_row = {'Cluster_ID': c_id, 'name': record['name']}
            # Fill in extra data
            for k in extra_keys:
                out_row[k] = record.get(k, '')
            writer.writerow(out_row)

if __name__ == "__main__":
    main()
