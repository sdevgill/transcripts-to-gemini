"""
Text Transcript to JSON Batch Converter
=======================================

Converts raw text transcript files (.txt) into structured JSON batches,
suitable for further processing or indexing.

Examples
--------
# Process transcripts into default batches of 10
python txt_to_batches.py --input_dir /path/to/transcripts --output_dir /path/to/batches

# Process transcripts into batches of 5
python txt_to_batches.py --input_dir /path/to/transcripts --output_dir /path/to/batches --batch_size 5
"""

import argparse
import json
import os
import re


def extract_data_from_filename(filename, index=None):
    match = re.match(r"(\d+)-", filename)
    file_number = int(match.group(1)) if match else (index if index is not None else 0)

    title = filename[:-4]
    title_match = re.match(r"\d+-#\d+\s*-\s*(.*)", title)
    if title_match:
        title = title_match.group(1).strip()

    return file_number, title


def process_files(input_dir, output_dir, batch_size):
    os.makedirs(output_dir, exist_ok=True)

    try:
        filenames = [f for f in os.listdir(input_dir) if f.lower().endswith(".txt")]
    except FileNotFoundError:
        print(f"Error: Input directory not found: {input_dir}")
        return 0

    numbered_files = []
    for i, filename in enumerate(filenames):
        file_number, _ = extract_data_from_filename(filename, index=i)
        numbered_files.append((file_number, filename, i))

    numbered_files.sort(key=lambda x: x[0])

    all_files = []
    error_count = 0
    for _, filename, original_idx in numbered_files:
        full_path = os.path.join(input_dir, filename)
        file_number, title = extract_data_from_filename(filename, index=original_idx)

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                transcript = f.read()
            all_files.append(
                {
                    "episode_number": file_number,
                    "title": title,
                    "transcript": transcript,
                    "filename": filename,
                }
            )
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            error_count += 1
            continue

    batch_count = 0
    for i in range(0, len(all_files), batch_size):
        batch_data = all_files[i : i + batch_size]
        batch_count += 1
        output_filename = f"batch_{batch_count:03d}.json"
        output_path = os.path.join(output_dir, output_filename)
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(batch_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error: Failed to write batch {output_filename}: {e}")

    print(f"Processed {len(all_files)} out of {len(filenames)} files.")
    if error_count > 0:
        print(f"Encountered errors reading {error_count} files.")
    return batch_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert podcast transcript txt files to JSON batches.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input_dir", required=True, help="Directory containing transcript .txt files."
    )
    parser.add_argument(
        "--output_dir", required=True, help="Directory to write JSON batch files."
    )
    parser.add_argument(
        "--batch_size", type=int, default=10, help="Number of files per batch file."
    )
    args = parser.parse_args()

    num_batches = process_files(args.input_dir, args.output_dir, args.batch_size)
    print(f"Wrote {num_batches} batch files.")


if __name__ == "__main__":
    main()
