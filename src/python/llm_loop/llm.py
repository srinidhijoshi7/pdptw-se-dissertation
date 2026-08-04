"""
Gemini API interaction and code extraction.

Kept separate from the driver so that swapping to a different LLM provider
(Claude, OpenAI, local Ollama) later requires changes only to this module.
"""
import hashlib
import os
import re
import sys

from dotenv import load_dotenv
from google import genai

import config


def call_llm(prompt: str) -> tuple[str, float]:
    """
    Send a prompt to Gemini and return (response_text, elapsed_seconds).
    """
    import time
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)
    t0 = time.time()
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )
    elapsed = time.time() - t0
    return response.text, elapsed


def extract_julia_code(response_text: str) -> str:
    """
    Pull Julia code out of a markdown-fenced response.

    Fallbacks (in preference order):
      1. ```julia ... ```
      2. ``` ... ```
      3. the whole response as-is
    """
    m = re.search(r"```julia\s*\n(.*?)```", response_text, re.DOTALL)
    if m:
        return m.group(1).strip()

    m = re.search(r"```\s*\n?(.*?)```", response_text, re.DOTALL)
    if m:
        return m.group(1).strip()

    return response_text.strip()


def short_hash(text: str) -> str:
    """12-char SHA256 prefix. Enough for uniquely identifying prompts/code in logs."""
    return hashlib.sha256(text.encode()).hexdigest()[:12]