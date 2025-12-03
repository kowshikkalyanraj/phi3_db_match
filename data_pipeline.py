#!/usr/bin/env python3
"""
data_pipeline.py
Runs the CSV -> DB -> AI pipeline using Phi-3 Mini 3.8B.
"""

import csv
import time
from typing import Dict, Any

from db_manager import init_db, get_existing_result, save_result
from ai_extractor import extract_with_ai

INPUT_CSV = "ocr_raw_labels.csv"
OUTPUT_CSV = "ocr_structured_output.csv"


def process_raw_text(raw_text: str, label_index: int = None) -> Dict[str, Any]:
    """Check DB first. If not present, call AI extractor and save result."""
    
    if label_index is not None:
        print(f"🧾 Label #{label_index}")

    # First check database
    existing = get_existing_result(raw_text)
    if existing:
        print("✅ Found in database")
        print(f"👤 Recipient Name: {existing['recipient_name']}")
        print(f"🏠 Address: {existing['address']}")
        return {
            "source": "database",
            "recipient_name": existing["recipient_name"],
            "address": existing["address"]
        }

    # Not in database → run AI
    print("🔍 Not found in database. Using AI extraction...")

    start = time.time()
    ai_out = extract_with_ai(raw_text)
    elapsed = ai_out.get("__inference_time", time.time() - start)

    recipient_name = ai_out.get("recipient_name") or ""
    address = ai_out.get("address") or ""
    verification_status = ai_out.get("verification_status", "unknown")
    candidate_id = ai_out.get("candidate_id", "")

    print("✅ Extracted with AI")
    print(f"⏱️  AI Inference Time: {elapsed:.2f}s")
    print(f"👤 Recipient Name: {recipient_name}")
    print(f"🏠 Address: {address}")
    print(f"🔒 Verification Status: {verification_status}")
    if candidate_id:
        print(f"🆔 Candidate ID: {candidate_id}")

    # Save into database (only if verified or if we want to save nulls? User said print nulls)
    # If verification failed, recipient_name and address are None/Empty.
    save_result(raw_text, recipient_name, address)
    print("💾 Saved to database")

    return {
        "source": "ai",
        "recipient_name": recipient_name,
        "address": address,
        "inference_time": elapsed,
        "verification_status": verification_status,
        "candidate_id": candidate_id
    }


def process_all():
    """Process CSV and write structured CSV."""
    init_db()
    rows = []

    with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for i, row in enumerate(reader, start=1):
            raw_text = row.get("raw_text", "").strip()
            if not raw_text:
                continue

            result = process_raw_text(raw_text, label_index=i)

            rows.append({
                "raw_text": raw_text,
                "recipient_name": result.get("recipient_name") or "",
                "address": result.get("address") or "",
                "source": result.get("source"),
                "verification_status": result.get("verification_status", ""),
                "candidate_id": result.get("candidate_id", "")
            })

            print("-" * 40)

    # Write output CSV
    with open(OUTPUT_CSV, "w", newline='', encoding='utf-8') as outfile:
        fieldnames = ["raw_text", "recipient_name", "address", "source", "verification_status", "candidate_id"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"✅ Pipeline complete! Results saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    process_all()
