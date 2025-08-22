#!/usr/bin/env python3
"""
extract_frame_500.py

Recursively find .mp4 files under INPUT_DIR and extract the 500th frame
(human counting, i.e. zero-based index 499) as PNGs into OUTPUT_DIR.

Usage:
  python extract_frame_500.py /path/to/input /path/to/output
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except Exception:
        sys.stderr.write("Error: ffmpeg is required but not installed or not on PATH.\n")
        sys.exit(1)

def extract_exact_frame(input_video: Path, output_png: Path, frame_index_zero_based: int) -> bool:
    """Extract exactly the frame at index frame_index_zero_based using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-hide_banner", "-loglevel", "error",
        "-y",
        "-i", str(input_video),
        "-vf", f"select='eq(n\\,{frame_index_zero_based})'",
        "-vframes", "1",
        "-vsync", "vfr",
        str(output_png),
    ]
    result = subprocess.run(cmd)
    return result.returncode == 0 and output_png.exists() and output_png.stat().st_size > 0

def main():
    parser = argparse.ArgumentParser(description="Extract the 500th frame from every .mp4 under a folder.")
    parser.add_argument("input_dir", type=Path, help="Root folder to search for .mp4 files (recursively).")
    parser.add_argument("output_dir", type=Path, help="Folder where extracted .png frames will be saved.")
    parser.add_argument("--frame", type=int, default=500,
                        help="Frame number to extract (human counting). Default: 500")
    parser.add_argument("--zero_based", action="store_true",
                        help="Interpret --frame as zero-based instead of human counting.")
    args = parser.parse_args()

    check_ffmpeg()

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.is_dir():
        sys.stderr.write(f"Error: input_dir is not a directory: {input_dir}\n")
        sys.exit(1)

    frame_index_zero_based = args.frame if args.zero_based else (args.frame - 1)

    videos = [p for p in input_dir.rglob("*.mp4")]
    if not videos:
        print("No .mp4 files found.")
        return

    print(f"Found {len(videos)} video(s). Extracting frame index {frame_index_zero_based}...")

    for vid in videos:
        out_png = output_dir / f"{vid.stem}.png"
        ok = extract_exact_frame(vid, out_png, frame_index_zero_based)
        if ok:
            print(f"[OK]  {vid} -> {out_png}")
        else:
            print(f"[SKIP] Could not extract (maybe fewer than {frame_index_zero_based+1} frames): {vid}", file=sys.stderr)

if __name__ == "__main__":
    main()
