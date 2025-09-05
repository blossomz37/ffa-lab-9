#!/usr/bin/env python3
"""
Quick analysis script for user content
Makes it easy to analyze your own writing with consistent output organization
"""

import sys
import os
from pathlib import Path
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: python quick_analyze.py your_chapter.txt [window_size]")
        print("Example: python quick_analyze.py samples/user_content/my_chapter.txt 3")
        return
    
    input_file = Path(sys.argv[1])
    window_size = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        return
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filenames based on input
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = input_file.stem
    
    csv_output = output_dir / f"{base_name}_emotions_{timestamp}.csv"
    json_output = output_dir / f"{base_name}_emotions_{timestamp}.json"
    
    # Run the analysis
    cmd = (f'python tools/chapter_emotion_arc.py "{input_file}" '
           f'--window {window_size} '
           f'--csv "{csv_output}" '
           f'--json "{json_output}"')
    
    print(f"Analyzing: {input_file}")
    print(f"Window size: {window_size}")
    print(f"Output files will be saved to: {output_dir}")
    print("-" * 50)
    
    os.system(cmd)
    
    print("-" * 50)
    print(f"Analysis complete!")
    print(f"CSV data: {csv_output}")
    print(f"JSON data: {json_output}")

if __name__ == "__main__":
    main()
