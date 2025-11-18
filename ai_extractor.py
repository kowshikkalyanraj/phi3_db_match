#!/usr/bin/env python3

import time
import json
import re
from typing import Dict, Optional
from import_ollama import get_ollama_client

OLLAMA_MODEL = "phi3:3.8b"

OPTIONS = {
    "temperature": 0.1,
    "top_p": 0.9,
    "repeat_penalty": 1.1,
    "num_predict": 150
}


def build_prompt(raw_text: str) -> str:
    return f"""
You are an expert at understanding extremely messy OCR shipping labels.

Extract ONLY:
1. Recipient Name (a PERSON'S NAME)
2. Full Address (Street + City + State + ZIP)

The text may contain:
- tracking numbers
- weights
- codes
- broken text
- misspellings
- noise like "fat1", "dsm1", "ups ground", etc.

RULES:
- Output ONLY JSON.
- "recipient_name" MUST be a human name (e.g., Zoey Dongs → Zoey Dong).
- "address" MUST be a valid U.S. postal address.
- If multiple names appear, pick the most human-like one.
- Ignore all tracking numbers, weights, IDs, barcodes.
- If unsure, make the best guess.
- If something is missing, return an empty string.

Example Output:
{{"recipient_name": "John Doe", "address": "2501 Pico Blvd, Santa Monica CA 90405"}}

Now extract from this text:

\"\"\"{raw_text}\"\"\"
"""


def extract_json(text: str) -> dict:
    # Extract the first JSON-like block
    match = re.search(r"\{[\s\S]*?\}", text)
    if match:
        block = match.group(0)
        # Clean common issues
        block = re.sub(r",\s*}", "}", block)
        block = re.sub(r",\s*\]", "]", block)
        try:
            return json.loads(block)
        except:
            return {}
    return {}


def clean(s: Optional[str]) -> Optional[str]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    return s


def fix_address(address: str) -> str:
    if not address:
        return ""

    address = address.replace("  ", " ").strip()

    # Common OCR address fixes
    address = address.replace(" ,", ",")
    address = re.sub(r"([A-Za-z])  ([A-Za-z])", r"\1 \2", address)

    # Fix missing comma before city
    address = re.sub(r",\s*([A-Za-z]{2}) ", r", \1 ", address)

    # Fix city/state/zip format
    address = re.sub(
        r"([a-zA-Z ]+)\s+([A-Z]{2})\s+(\d{5}(-\d{4})?)",
        lambda m: f"{m.group(1).title()}, {m.group(2)} {m.group(3)}",
        address,
    )

    return address


def extract_with_ai(raw_text: str) -> Dict[str, Optional[str]]:
    client = get_ollama_client()
    prompt = build_prompt(raw_text)

    start = time.time()
    resp = client.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options=OPTIONS
    )
    elapsed = time.time() - start

    # Extract text response
    content = ""
    if "message" in resp and "content" in resp["message"]:
        content = resp["message"]["content"]
    else:
        # fallback
        try:
            content = resp["choices"][0]["message"]["content"]
        except:
            content = str(resp)

    parsed = extract_json(content)
    name = clean(parsed.get("recipient_name"))
    address = fix_address(clean(parsed.get("address"))) if parsed.get("address") else ""

    return {
        "recipient_name": name or "",
        "address": address or "",
        "__raw_ai_output": content,
        "__inference_time": elapsed
    }
