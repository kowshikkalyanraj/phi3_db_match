#!/usr/bin/env python3
"""
setup_model.py
One-time setup helper: checks if Ollama is reachable and instructs how to pull the model.
"""

import subprocess
import sys
from import_ollama import OLLAMA_ENDPOINT, get_ollama_client

MODEL = "phi3:3.8b"

def check_ollama():
    try:
        client = get_ollama_client()
        # quick call to check connectivity
        tags = client.tags()
        print("✅ Ollama reachable.")
        return True
    except Exception as e:
        print("❌ Could not reach Ollama. Ensure `ollama serve` is running.")
        print("Error:", e)
        return False

def instruct_pull():
    print(f"Please pull the model once (terminal):\n\n  ollama pull {MODEL}\n")
    print("Then run:\n  export OLLAMA_KEEP_ALIVE=5m\n  python optimize_for_speed.py\n")

if __name__ == "__main__":
    ok = check_ollama()
    instruct_pull()
