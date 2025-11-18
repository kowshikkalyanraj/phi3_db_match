"""
import_ollama.py
Simple wrapper to create and return an Ollama client consistently across files.
"""

import os
import time

# import ollama (the python package)
try:
    import ollama
except Exception as e:
    raise RuntimeError("Please install 'ollama' python package. pip install ollama") from e

OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")


def get_ollama_client():
    """
    Returns an Ollama client object. Keep this function in one place to allow consistent
    configuration and future mocking in tests.
    """
    client = ollama.Client(host=OLLAMA_ENDPOINT)
    return client
