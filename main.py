#!/usr/bin/env python3
"""
main.py
Entry point for interactive usage.
"""

from data_pipeline import process_all, process_raw_text
from db_manager import init_db

def interactive():
    init_db()
    print("🚀 Phi-3 Mini 3.8B enabled")
    while True:
        try:
            ans = input("Would you like to enter raw OCR text manually? (y/n): ").strip().lower()
            if ans in ("n", "no"):
                break
            raw = input("Enter raw text: ").strip()
            if not raw:
                continue
            result = process_raw_text(raw)
            if result["source"] == "database":
                print(f"✅ Found in database\n👤 Recipient Name: {result['recipient_name']}\n🏠 Address: {result['address']}\n📍 Source: Database")
            elif result["source"] == "ai":
                print(f"✅ Extracted with AI\n👤 Recipient Name: {result['recipient_name']}\n🏠 Address: {result['address']}\n📍 Source: AI\n⏱️  AI Inference Time: {result.get('inference_time', 0):.2f}s")
            else:
                print("⚠️ Extraction failed or returned no data.")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    # If you want to run batch processing:
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument("--batch", action="store_true", help="Process input CSV in batch mode")
    args = p.parse_args()
    if args.batch:
        process_all()
    else:
        interactive()
            