#!/usr/bin/env python3
"""
test_performance.py
Quick script to benchmark inference times on a small set of samples.
"""

import time
from ai_extractor import extract_with_ai

SAMPLES = [
    "Ship To: Joshua Ramsayys, 2501 Pico Blvd, Santa Monica CA 90405-1832",
    "Recipient: Zoey Dong, 2821 Carradale Dr, Roseville, CA 95661",
    "To: Syta Saephan, 8150 Sierra College Blvd Ste, Roseville, CA 95661"
]

def run():
    times = []
    for s in SAMPLES:
        start = time.time()
        out = extract_with_ai(s)
        t = out.get("__inference_time", time.time() - start)
        times.append(t)
        print("Input:", s)
        print("Output:", out.get("recipient_name"), "|", out.get("address"))
        print(f"Inference time: {t:.2f}s")
        print("-"*30)
    avg = sum(times)/len(times)
    print(f"Average inference time: {avg:.2f}s")

if __name__ == "__main__":
    run()
