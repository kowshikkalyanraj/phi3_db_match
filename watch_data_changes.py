#!/usr/bin/env python3
"""
watch_data_changes.py
Simple CSV watcher: checks the mtime of input CSV and triggers the pipeline when file changes.
"""

import os
import time
from data_pipeline import process_all

INPUT = "ocr_raw_labels.csv"
POLL_INTERVAL = 2.0  # seconds

def watch():
    last_mtime = None
    if os.path.exists(INPUT):
        last_mtime = os.path.getmtime(INPUT)
    print(f"Watching {INPUT} for changes...")
    try:
        while True:
            if os.path.exists(INPUT):
                m = os.path.getmtime(INPUT)
                if last_mtime is None or m > last_mtime:
                    print("Change detected. Running pipeline...")
                    process_all()
                    last_mtime = m
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Watcher stopped.")

if __name__ == "__main__":
    watch()
