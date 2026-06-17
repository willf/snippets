# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "datasets",
#     "pillow",
#     "huggingface-hub"
# ]
# ///

import os
import argparse
from datasets import load_dataset


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Load a local directory of images and push it to the Hugging Face Hub."
    )
    parser.add_argument(
        "image_dir",
        type=str,
        help="Path to the local directory containing your images.",
    )
    parser.add_argument(
        "repo_id",
        type=str,
        help="Target Hugging Face repository ID (e.g., 'username/my_awesome_images').",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Include this flag to make the dataset private. Defaults to public.",
    )

    args = parser.parse_args()

    print(f"Loading images from '{args.image_dir}'...")

    # Load dataset
    try:
        dataset = load_dataset("imagefolder", data_dir=args.image_dir)
    except Exception as e:
        print(f"❌ Failed to load dataset: {e}")
        return

    print("\nDataset structure:")
    print(dataset)

    print(
        f"\nPushing dataset to the Hub: https://huggingface.co/datasets/{args.repo_id}"
    )
    print(f"Visibility: {'Private' if args.private else 'Public'}")

    # Push to Hub
    try:
        dataset.push_to_hub(args.repo_id, private=args.private)
        print("\n✅ Upload complete!")
    except Exception as e:
        print(f"\n❌ Failed to push to hub: {e}")


if __name__ == "__main__":
    main()
