"""
LLM evolution driver — minimum viable version.

Runs one full cycle end-to-end:
    prompt -> Gemini -> Julia code -> write to candidates/current.jl
    -> MSLP -> parse cost -> append to logs/candidates.jsonl

This is NOT yet an evolution loop. That comes next.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai

import config


# ============================================================
# Step 1: Load prompt
# ============================================================
def load_prompt() -> str:
    if not config.PROMPT_FILE.exists():
        sys.exit(f"Prompt file not found: {config.PROMPT_FILE}")
    return config.PROMPT_FILE.read_text()


# ============================================================
# Step 2: Call Gemini
# ============================================================
def call_gemini(prompt: str) -> str:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        sys.exit("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=prompt,
    )
    return response.text


# ============================================================
# Step 3: Extract Julia code from response
# ============================================================
def extract_julia_code(response_text: str) -> str:
    """
    Pull the Julia code out of a markdown-fenced response.
    Tries three fallbacks in order of preference.
    """
    # 3a: fenced with ```julia
    match = re.search(r"```julia\s*\n(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 3b: any fenced block
    match = re.search(r"```\s*\n?(.*?)```", response_text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # 3c: no fences — hope the whole response is code
    return response_text.strip()


# ============================================================
# Step 4: Write candidate file
# ============================================================
def write_candidate(code: str) -> None:
    config.CANDIDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.CANDIDATE_FILE.write_text(code)


# ============================================================
# Step 5: Run MSLP subprocess
# ============================================================
def run_mslp() -> tuple[int, str, str]:
    """
    Returns (exit_code, stdout, stderr). Times out after JULIA_TIMEOUT.
    """
    cmd = [
        "julia", "pdptwse.jl",
        "--inst_path", config.INSTANCE_REL_PATH,
        "--cut_off_machs", "4",
        "--method_type", "heur",
        "--method_code", "mslp",
        "--seed", str(config.SEED),
        "--greedy_service_order", "llm_candidate",
        "--alpha", str(config.ALPHA),
        "--threads", "1",
        "--output_flag_grb_MSLP", "0",
        "--mslpa", str(config.MSLP_ITERS),
        "--mslpr", "I",
        "--max_time", str(config.MAX_TIME),
        "--output", "./logs/",
        "--print_sol", "0",
        "--solver_method", "A",
    ]

    env = os.environ.copy()
    env["LLM_CANDIDATE_FILE"] = str(config.CANDIDATE_FILE)

    try:
        result = subprocess.run(
            cmd,
            cwd=config.JULIA_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=config.JULIA_TIMEOUT,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "TIMEOUT"


# ============================================================
# Step 6: Parse best cost from MSLP output
# ============================================================
def parse_best_cost(mslp_stdout: str) -> float | None:
    """
    MSLP prints 'Best solution value: XXX' near the end.
    Returns the cost as float, or None if not found.
    """
    match = re.search(r"Best solution value:\s*([\d.]+)", mslp_stdout)
    if match:
        return float(match.group(1))
    return None


# ============================================================
# Step 7: Append log entry
# ============================================================
def log_result(entry: dict) -> None:
    config.CANDIDATES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.CANDIDATES_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ============================================================
# Main
# ============================================================
def main() -> None:
    print("=" * 60)
    print("LLM Evolution Driver — single cycle")
    print("=" * 60)

    # --- Load prompt ---
    print("\n[1] Loading prompt...")
    prompt = load_prompt()
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:12]
    print(f"    Prompt hash: {prompt_hash}  ({len(prompt)} chars)")

    # --- Call Gemini ---
    print(f"\n[2] Calling Gemini ({config.GEMINI_MODEL})...")
    t0 = time.time()
    response_text = call_gemini(prompt)
    llm_elapsed = time.time() - t0
    print(f"    Response received in {llm_elapsed:.1f}s ({len(response_text)} chars)")

    # --- Extract code ---
    print("\n[3] Extracting Julia code from response...")
    code = extract_julia_code(response_text)
    code_hash = hashlib.sha256(code.encode()).hexdigest()[:12]
    print(f"    Extracted {len(code)} chars, hash: {code_hash}")
    print("    --- CODE PREVIEW ---")
    for line in code.splitlines()[:10]:
        print(f"    {line}")
    if len(code.splitlines()) > 10:
        print(f"    ... ({len(code.splitlines()) - 10} more lines)")
    print("    --- END PREVIEW ---")

    # --- Write candidate ---
    print(f"\n[4] Writing candidate to {config.CANDIDATE_FILE.name}...")
    write_candidate(code)

    # --- Run MSLP ---
    print(f"\n[5] Running MSLP (timeout {config.JULIA_TIMEOUT}s)...")
    t0 = time.time()
    exit_code, stdout, stderr = run_mslp()
    mslp_elapsed = time.time() - t0
    print(f"    Julia exited with code {exit_code} in {mslp_elapsed:.1f}s")

    # --- Parse cost ---
    print("\n[6] Parsing best cost...")
    cost = parse_best_cost(stdout)
    if cost is not None:
        print(f"    Best cost: {cost}")
    else:
        print("    Could not parse cost — MSLP likely errored")
        # Show last 20 lines of stdout for quick diagnosis
        print("    Last stdout lines:")
        for line in stdout.splitlines()[-20:]:
            print(f"      {line}")
        if stderr:
            print("    Last stderr lines:")
            for line in stderr.splitlines()[-10:]:
                print(f"      {line}")

    # --- Log ---
    print("\n[7] Appending log entry...")
    entry = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "model":           config.GEMINI_MODEL,
        "prompt_hash":     prompt_hash,
        "code_hash":       code_hash,
        "code":            code,
        "instance":        config.INSTANCE_REL_PATH.split("/")[-1],
        "seed":            config.SEED,
        "cost":            cost,
        "exit_code":       exit_code,
        "llm_elapsed_s":   round(llm_elapsed, 2),
        "mslp_elapsed_s":  round(mslp_elapsed, 2),
    }
    log_result(entry)
    print(f"    Written to {config.CANDIDATES_LOG.name}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("CYCLE COMPLETE")
    print("=" * 60)
    print(f"Cost:      {cost}")
    print(f"Baseline (random, same seed): 763.79")
    if cost is not None:
        delta = cost - 763.79
        symbol = "▼" if delta < 0 else "▲" if delta > 0 else "="
        print(f"Delta:     {symbol} {abs(delta):.2f}")


if __name__ == "__main__":
    main()