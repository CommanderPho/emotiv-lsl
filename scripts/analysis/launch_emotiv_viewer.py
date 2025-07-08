#!/usr/bin/env python3
import sys
import mne
from pathlib import Path

def main():
    if len(sys.argv) != 2:
        print("Usage: python launch_emotiv_viewer.py <data_file.fif>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)
    
    print(f"Loading {file_path}...")
    raw = mne.io.read_raw_fif(file_path)
    
    # Basic preprocessing for better visualization
    raw.filter(l_freq=0.5, h_freq=40)  # Optional filtering
    
    print("Launching MNE-Qt-Browser...")
    raw.plot()

if __name__ == "__main__":
    main()