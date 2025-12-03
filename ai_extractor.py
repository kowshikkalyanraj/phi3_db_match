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
- "recipient_name": The person receiving the package. Often found at the END of the text.
- "address": The full delivery address (Street, City, State, Zip).
- The address might be broken into parts. Combine them.
- Ignore "Sender" or "From" addresses if possible.
- Ignore tracking numbers, weights, and codes like "fat1", "dsm1".
- If the name is misspelled (e.g. "Zoey Dongs"), fix it ("Zoey Dong").

Example 1:
Input: "2821 carradale dr, 95661 roseville, ca, zoey dongs"
Output: {{"recipient_name": "Zoey Dong", "address": "2821 Carradale Dr, Roseville, CA 95661"}}

Example 2:
Input: "ship to, 8150 sierra college blvd, roseville ca, syta saephan"
Output: {{"recipient_name": "Syta Saephan", "address": "8150 Sierra College Blvd, Roseville, CA"}}

Now extract from:
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

    # Verification Step
    verified_result = verify_against_db(name, address)
    
    if verified_result:
        return {
            "recipient_name": verified_result["recipient_name"],
            "address": verified_result["address"],
            "__raw_ai_output": content,
            "__inference_time": elapsed,
            "verification_status": "verified",
            "candidate_id": verified_result["candidate_id"]
        }
    else:
        return {
            "recipient_name": None,
            "address": None,
            "__raw_ai_output": content,
            "__inference_time": elapsed,
            "verification_status": "failed"
        }


def load_candidate_db(db_path: str = "candidate_db.json") -> list:
    try:
        with open(db_path, 'r') as f:
            data = json.load(f)
            return data.get("recipients", [])
    except FileNotFoundError:
        print(f"Warning: {db_path} not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding {db_path}.")
        return []


def verify_against_db(extracted_name: Optional[str], extracted_address: Optional[str]) -> Optional[Dict[str, str]]:
    if not extracted_name or not extracted_address:
        return None

    candidates = load_candidate_db()
    
    # Normalize for comparison
    def normalize_str(s: str) -> str:
        # Remove punctuation and extra spaces, lower case
        s = re.sub(r'[^\w\s]', '', s)
        return re.sub(r'\s+', ' ', s).strip().lower()

    norm_name = normalize_str(extracted_name)
    norm_addr = normalize_str(extracted_address)

    for candidate in candidates:
        # Check Name (First + Last or Preferred Full Name)
        cand_first = candidate.get("first_name", "")
        cand_last = candidate.get("last_name", "")
        cand_full = f"{cand_first} {cand_last}"
        cand_pref = candidate.get("preferred_full_name", "")

        norm_cand_full = normalize_str(cand_full)
        norm_cand_pref = normalize_str(cand_pref)

        name_match = (norm_name == norm_cand_full) or (norm_name == norm_cand_pref)
        
        # Check Address
        cand_addr = candidate.get("address", "")
        norm_cand_addr = normalize_str(cand_addr)
        
        # Token-based matching
        extracted_tokens = set(norm_addr.split())
        candidate_tokens = set(norm_cand_addr.split())
        
        if not extracted_tokens:
            address_match = False
        else:
            common_tokens = extracted_tokens.intersection(candidate_tokens)
            match_ratio = len(common_tokens) / len(extracted_tokens)
            # Threshold: 70% of extracted tokens must be in candidate
            address_match = match_ratio >= 0.7

        if name_match and address_match:
            return {
                "recipient_name": candidate.get("preferred_full_name") or f"{candidate.get('first_name')} {candidate.get('last_name')}",
                "address": candidate.get("address"),
                "candidate_id": candidate.get("recipient_id")
            }

    return None

