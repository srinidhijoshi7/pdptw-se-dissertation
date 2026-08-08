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

    Retries on:
      - 429 (rate limit): waits per retry_delay hint, then retries once
      - 503 (server unavailable): waits 20s, retries up to 3 times
    Raises on any other error or if all retries exhausted.
    """
    import time
    from google.genai import errors as genai_errors

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)

    max_503_retries = 3
    t0 = time.time()

    for attempt in range(max_503_retries + 1):
        try:
            response = client.models.generate_content(
                model=config.GEMINI_MODEL,
                contents=prompt,
            )
            elapsed = time.time() - t0
            return response.text, elapsed

        except (genai_errors.ClientError, genai_errors.ServerError) as e:
            err_str = str(e)

            # 429 = rate limit (client error)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                import re
                m = re.search(r"retry in ([\d.]+)s", err_str)
                wait_s = float(m.group(1)) + 2 if m else 60
                print(f"    ⚠ Rate limit (429). Sleeping {wait_s:.0f}s then retrying...")
                time.sleep(wait_s)
                # Retry once for 429
                response = client.models.generate_content(
                    model=config.GEMINI_MODEL,
                    contents=prompt,
                )
                elapsed = time.time() - t0
                return response.text, elapsed

            # 503 = server busy (transient)
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                if attempt < max_503_retries:
                    wait_s = 20 * (attempt + 1)   # 20s, 40s, 60s
                    print(f"    ⚠ Server busy (503) attempt {attempt+1}/{max_503_retries}. Sleeping {wait_s}s then retrying...")
                    time.sleep(wait_s)
                    continue
                else:
                    print(f"    ⚠ Server still busy after {max_503_retries} retries — giving up.")
                    raise

            else:
                raise

    # Shouldn't reach here but keeps the type checker happy
    raise RuntimeError("Retry loop exited without returning or raising")


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
def load_seed_prompt() -> str:
    if not config.PROMPT_FILE.exists():
        raise SystemExit(f"Seed prompt not found: {config.PROMPT_FILE}")
    return config.PROMPT_FILE.read_text()


def build_evolve_prompt(best_code: str, best_fitness: float) -> str:
    """
    Load the evolution template and substitute the current best candidate.
    """
    if not config.EVOLVE_PROMPT_FILE.exists():
        raise SystemExit(f"Evolve prompt not found: {config.EVOLVE_PROMPT_FILE}")
    template = config.EVOLVE_PROMPT_FILE.read_text()
    return (
        template
        .replace("{{BEST_CODE}}", best_code)
        .replace("{{BEST_FITNESS}}", f"{best_fitness:.4f}")
    )
def build_diversify_prompt(best_code: str, best_fitness: float, stagnation_gens: int) -> str:
    """
    Load the diversify template and substitute the champion + stagnation count.
    Used when the champion hasn't improved for STAGNATION_THRESHOLD generations.
    """
    if not config.DIVERSIFY_PROMPT_FILE.exists():
        raise SystemExit(f"Diversify prompt not found: {config.DIVERSIFY_PROMPT_FILE}")
    template = config.DIVERSIFY_PROMPT_FILE.read_text()
    return (
        template
        .replace("{{BEST_CODE}}", best_code)
        .replace("{{BEST_FITNESS}}", f"{best_fitness:.4f}")
        .replace("{{STAGNATION_GENS}}", str(stagnation_gens))
    )