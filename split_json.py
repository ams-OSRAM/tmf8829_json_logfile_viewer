#!/usr/bin/env python3

# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES.TXT                                     *
# *****************************************************************************

'''
Split TMF8829 JSON log file into multiple parts
'''

import json
import argparse
import os
import gzip

def split_json(input_file, output_dir=None, frames_per_file=50):
    """Split JSON file into multiple parts

    Args:
        input_file: Path to input JSON file (can be .json.gz for compressed files)
        output_dir: Directory to save output files (default: same as input file)
        frames_per_file: Number of frames per output file (default: 50)
    """
    # Determine if input file is compressed
    is_compressed = input_file.endswith('.gz')

    # Load the original JSON file
    open_func = gzip.open if is_compressed else open
    mode = 'rt' if is_compressed else 'r'

    with open_func(input_file, mode, encoding='utf-8') as f:
        data = json.load(f)

    # Get result set
    result_set = data.get('Result_Set', [])

    total_frames = len(result_set)

    print(f"Total frames in original file: {total_frames}")
    print(f"Frames per output file: {frames_per_file}")

    # Determine output directory
    if output_dir is None:
        output_dir = os.path.dirname(input_file)

    # Create output filenames
    input_dir, input_filename = os.path.split(input_file)
    input_basename, input_ext = os.path.splitext(input_filename)

    # Calculate number of parts
    num_parts = (total_frames + frames_per_file - 1) // frames_per_file

    print(f"Will create {num_parts} output file(s)")

    output_files = []
    total_size = 0

    # Determine output extension
    output_ext = '.json.gz' if is_compressed else '.json'

    # Split into multiple parts
    for i in range(num_parts):
        start_idx = i * frames_per_file
        end_idx = min((i + 1) * frames_per_file, total_frames)

        # Create data for this part
        data_part = data.copy()
        data_part['Result_Set'] = result_set[start_idx:end_idx]

        # Create output filename
        output_file = os.path.join(output_dir, f"{input_basename}_part{i+1}{output_ext}")

        # Write the part (compressed if input was compressed)
        write_func = gzip.open if is_compressed else open
        write_mode = 'wt' if is_compressed else 'w'

        with write_func(output_file, write_mode, encoding='utf-8') as f:
            json.dump(data_part, f, indent=2, ensure_ascii=False)

        # Get file size
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        total_size += file_size
        output_files.append(output_file)

        # Print info
        num_frames = end_idx - start_idx
        print(f"✓ Created part {i+1}: {output_file}")
        print(f"  Frames: {start_idx} to {end_idx-1} ({num_frames} frames)")
        print(f"  Size: {file_size:.2f} MB")

    # Show summary
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    print(f"\n Summary:")
    print(f"  Original file: {input_filename} ({original_size:.2f} MB, {total_frames} frames)")
    print(f"  Created {num_parts} output file(s)")
    for i, output_file in enumerate(output_files):
        file_size = os.path.getsize(output_file) / (1024 * 1024)
        start_idx = i * frames_per_file
        end_idx = min((i + 1) * frames_per_file, total_frames)
        print(f"  Part {i+1}: {end_idx - start_idx} frames ({file_size:.2f} MB)")
    print(f"  Total output size: {total_size:.2f} MB")

def main():
    parser = argparse.ArgumentParser(description='Split TMF8829 JSON log file into multiple parts')
    parser.add_argument('-i', '--input', required=True,
                       help='Path to input JSON file (supports both .json and .json.gz)')
    parser.add_argument('-o', '--output-dir', help='Output directory (default: same as input file)')
    parser.add_argument('-n', '--frames-per-file', type=int, default=50,
                       help='Number of frames per output file (default: 50)')
    args = parser.parse_args()

    split_json(args.input, args.output_dir, args.frames_per_file)

if __name__ == "__main__":
    main()
