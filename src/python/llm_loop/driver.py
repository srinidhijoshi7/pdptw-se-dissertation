"""
LLM evolution driver — single-cycle version (Phase 7b refactor).

Runs one full cycle end-to-end for one prompt:
    prompt -> Gemini -> Julia code -> multi-instance evaluation -> log

Phase 7d will add the 1+lambda evolution loop on top of these primitives.
"""
import json
from dataclasses import asdict
from datetime import datetime, timezone

import config
from llm import call_llm, extract_julia_code, short_hash
from evaluator import evaluate


def load_prompt() -> str:
    if not config.PROMPT_FILE.exists():
        raise SystemExit(f"Prompt file not found: {config.PROMPT_FILE}")
    return config.PROMPT_FILE.read_text()


def log_candidate(entry: dict) -> None:
    config.CANDIDATES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.CANDIDATES_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    print("=" * 60)
    print(f"LLM Driver — single cycle (mode: {config.MODE})")
    print(f"Instance grid: {len(config.INSTANCE_GRID)} instance(s)")
    print("=" * 60)

    # 1. Prompt
    prompt = load_prompt()
    p_hash = short_hash(prompt)
    print(f"\n[1] Prompt loaded  ({len(prompt)} chars, hash {p_hash})")

    # 2. LLM
    print(f"\n[2] Calling Gemini ({config.GEMINI_MODEL})...")
    response, llm_elapsed = call_llm(prompt)
    print(f"    Response: {len(response)} chars in {llm_elapsed:.1f}s")

    # 3. Extract
    code = extract_julia_code(response)
    c_hash = short_hash(code)
    print(f"\n[3] Extracted code: {len(code)} chars, hash {c_hash}")

    # 4. Evaluate
    print(f"\n[4] Evaluating on {len(config.INSTANCE_GRID)} instance(s)...")
    result = evaluate(code)

    for r in result.per_instance:
        ratio_str = f"{r.ratio:.4f}" if r.ratio is not None else "FAILED"
        cost_str = f"{r.cost:.2f}" if r.cost is not None else "n/a"
        print(f"    {r.instance:45s}  cost={cost_str:>10s}  ratio={ratio_str}")

    fitness_str = f"{result.fitness:.4f}" if result.fitness != float("inf") else "inf (failed)"
    print(f"\n    Fitness (mean ratio): {fitness_str}")
    print(f"    Total elapsed: {result.total_elapsed_s}s")

    # 5. Log
    entry = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "model":           config.GEMINI_MODEL,
        "mode":            config.MODE,
        "prompt_hash":     p_hash,
        "code_hash":       c_hash,
        "code":            code,
        "fitness":         result.fitness if result.fitness != float("inf") else None,
        "all_succeeded":   result.all_succeeded,
        "per_instance":    [asdict(r) for r in result.per_instance],
        "llm_elapsed_s":   round(llm_elapsed, 2),
        "total_elapsed_s": result.total_elapsed_s,
    }
    log_candidate(entry)
    print(f"\n[5] Logged to {config.CANDIDATES_LOG.name}")

    print("\n" + "=" * 60)
    print("CYCLE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()