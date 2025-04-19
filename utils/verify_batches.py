"""
JSON Batch Verification Tool
===========================

Verifies that all transcript files were properly processed into JSON batches.
Identifies duplicates, missing files, and provides a summary of the processed files.

Examples
--------
# Verify JSON batches in a directory
python verify_batches.py --batch_dir /path/to/batches

"""

import argparse
import json
import os


def verify_batches(batch_dir):
    files = []
    batch_files = sorted([f for f in os.listdir(batch_dir) if f.endswith(".json")])

    if not batch_files:
        print(f"Error: No batch files found in {batch_dir}")
        return

    print(f"Found {len(batch_files)} batch files.")

    for batch_file in batch_files:
        path = os.path.join(batch_dir, batch_file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                batch_data = json.load(f)

            for file_entry in batch_data:
                files.append(
                    (
                        file_entry["episode_number"],
                        file_entry["title"],
                        file_entry["filename"],
                    )
                )
        except Exception as e:
            print(f"Error reading {batch_file}: {e}")

    total_files = len(files)
    print(f"Total files found: {total_files}")

    files.sort(key=lambda x: x[0])

    file_nums = [file_data[0] for file_data in files]
    file_set = set(file_nums)
    duplicates = len(file_nums) - len(file_set)

    if duplicates > 0:
        print(f"Warning: Found {duplicates} duplicate file numbers.")
        dup_dict = {}
        for num in file_nums:
            dup_dict[num] = dup_dict.get(num, 0) + 1
        print("Duplicated file numbers:", [k for k, v in dup_dict.items() if v > 1])

    if files:
        min_file = min(file_nums)
        max_file = max(file_nums)
        expected_range = set(range(min_file, max_file + 1))
        missing = expected_range - file_set

        if missing:
            print(
                f"Warning: Missing {len(missing)} files in the range {min_file}-{max_file}:"
            )
            if len(missing) < 50:
                print(sorted(list(missing)))
        else:
            print(f"Success: All files in range {min_file}-{max_file} are present.")

    print("\nFirst 5 files:")
    for i in range(min(5, len(files))):
        print(f"  {files[i][0]}: {files[i][1]}")

    print("\nLast 5 files:")
    for i in range(max(0, len(files) - 5), len(files)):
        print(f"  {files[i][0]}: {files[i][1]}")


def main():
    parser = argparse.ArgumentParser(description="Verify JSON batch files.")
    parser.add_argument(
        "--batch_dir", required=True, help="Directory containing JSON batch files."
    )
    args = parser.parse_args()

    verify_batches(args.batch_dir)


if __name__ == "__main__":
    main()
