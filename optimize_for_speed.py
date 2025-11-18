#!/usr/bin/env python3
"""
optimize_for_speed.py
Pre-warm the model to avoid cold-start delays and test a simple extraction to ensure
inference times are reasonable.
"""

import time
from import_ollama import get_ollama_client
MODEL = "phi3:3.8b"

def prewarm():
    client = get_ollama_client()
    prompt = "Warm up. Return a tiny JSON: {\"ok\":true}"
    start = time.time()
    try:
        resp = client.chat(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature":0.1, "num_predict": 20}
        )
        elapsed = time.time() - start
        print(f"Pre-warm done. Time: {elapsed:.2f}s")
        return elapsed
    except Exception as e:
        print("Pre-warm failed:", e)
        return None

if __name__ == "__main__":
    prewarm()
