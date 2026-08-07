# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "datasets>=4.6.0",
#     "rich>=14.2.0",
# ]
# ///

import argparse
import json
import sys
from datasets import load_dataset
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

# Initialize the Rich console to always use stderr
error_console = Console(stderr=True)


def get_columns(ds, requested_columns):
    available_columns = list(ds.features.keys())
    if not requested_columns:
        return available_columns
    return [c for c in requested_columns if c in available_columns]


def run_dry_run(repo_id, split):
    try:
        ds = load_dataset(repo_id, split=split, streaming=True)
        features = ds.features

        tree = Tree(f"[bold magenta]Dataset ID:[/bold magenta] {repo_id}")
        split_node = tree.add(f"[bold cyan]Split:[/bold cyan] {split}")
        columns_node = split_node.add("[bold yellow]Columns & Types[/bold yellow]")

        for col_name, dtype in features.items():
            columns_node.add(f"[green]{col_name}[/green]: [dim]{dtype}[/dim]")

        error_console.print(Panel(tree, title="Dry Run Summary", expand=False))

    except Exception as e:
        error_console.print(f"[bold red]Dry Run Error:[/bold red] {e}")
        sys.exit(1)


def stream_to_jsonl(repo_id, columns, offset, limit, split, shuffle, seed):
    try:
        ds = load_dataset(repo_id, split=split, streaming=True)

        if shuffle:
            error_console.print(
                f"[dim italic]Shuffling with seed {seed}...[/dim italic]"
            )
            ds = ds.shuffle(seed=seed, buffer_size=10_000)

        target_columns = get_columns(ds, columns)
        iterable_ds = ds.skip(offset).take(limit).select_columns(target_columns)

        for example in iterable_ds:
            # Output data to standard STDOUT
            sys.stdout.write(json.dumps(example) + "\n")
            sys.stdout.flush()

    except Exception as e:
        error_console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HF Dataset Streamer")
    parser.add_argument("repo", help="HF dataset ID")
    parser.add_argument("-c", "--columns", nargs="+", help="Columns to include")
    parser.add_argument("-o", "--offset", type=int, default=0, help="Rows to skip")
    parser.add_argument(
        "-n", "--limit", type=int, default=sys.maxsize, help="Rows to fetch"
    )
    parser.add_argument("-s", "--split", default="train", help="Dataset split")
    parser.add_argument("--shuffle", action="store_true", help="Shuffle the stream")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for shuffle")
    parser.add_argument(
        "--dry-run", action="store_true", help="Describe dataset and exit"
    )

    args = parser.parse_args()

    if args.dry_run:
        run_dry_run(args.repo, args.split)
    else:
        stream_to_jsonl(
            args.repo,
            args.columns,
            args.offset,
            args.limit,
            args.split,
            args.shuffle,
            args.seed,
        )
