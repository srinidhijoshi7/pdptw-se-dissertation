"""
LLM evolution driver — 1+lambda loop (Phase 7d).

Generation 0: seed prompt -> initial champion.
Generation 1..N: for each generation, generate LAMBDA candidates using the
evolve prompt (which shows the current champion + fitness); if any beats the
champion, it replaces the champion.

All candidates are logged to candidates.jsonl.
Generation summaries are logged to generations.jsonl.
"""
import json
from dataclasses import asdict
from datetime import datetime, timezone

import config
from llm import (
    call_llm,
    extract_julia_code,
    short_hash,
    load_seed_prompt,
    build_evolve_prompt,
    build_diversify_prompt,
)
from evaluator import evaluate, EvaluationResult


# ============================================================
# Logging
# ============================================================
def log_candidate(entry: dict) -> None:
    config.CANDIDATES_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.CANDIDATES_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def log_generation(entry: dict) -> None:
    config.GENERATIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.GENERATIONS_LOG.open("a") as f:
        f.write(json.dumps(entry) + "\n")


# ============================================================
# One candidate: prompt -> LLM -> extract -> evaluate -> log
# ============================================================
def produce_and_evaluate(
    prompt: str,
    generation: int,
    slot: int,
    parent_hash: str | None,
) -> tuple[str, EvaluationResult, str]:
    """
    Run one candidate through the pipeline. Returns (code, eval_result, code_hash).
    """
    p_hash = short_hash(prompt)
    print(f"  [gen {generation} slot {slot}] Calling Gemini...")
    response, llm_elapsed = call_llm(prompt)
    code = extract_julia_code(response)
    c_hash = short_hash(code)
    print(f"  [gen {generation} slot {slot}] Code hash: {c_hash}, LLM {llm_elapsed:.1f}s")

    print(f"  [gen {generation} slot {slot}] Evaluating on {len(config.INSTANCE_GRID)} instance(s)...")
    result = evaluate(code)

    fitness_str = f"{result.fitness:.4f}" if result.fitness != float("inf") else "inf"
    print(f"  [gen {generation} slot {slot}] Fitness: {fitness_str}  ({result.total_elapsed_s}s)")

    entry = {
        "timestamp":       datetime.now(timezone.utc).isoformat(),
        "generation":      generation,
        "slot":            slot,
        "parent_hash":     parent_hash,
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
    return code, result, c_hash


# ============================================================
# Main evolution loop
# ============================================================
def main() -> None:
    print("=" * 70)
    print(f"LLM Evolution Loop — 1+lambda  (mode: {config.MODE})")
    print(f"lambda = {config.LAMBDA}, generations = {config.NUM_GENERATIONS}")
    print(f"Instance grid: {len(config.INSTANCE_GRID)} instance(s)")
    print("=" * 70)

    # ----- Generation 0: load champion seed OR call seed prompt -----
    print(f"\n{'='*70}\nGeneration 0 (seed)\n{'='*70}")

    if config.CHAMPION_SEED_FILE.exists():
        print(f"Loading champion seed from {config.CHAMPION_SEED_FILE.name}")
        code = config.CHAMPION_SEED_FILE.read_text()
        # Strip metadata header comment lines (starting with #) if present
        code_lines = code.splitlines()
        while code_lines and code_lines[0].strip().startswith("#"):
            code_lines.pop(0)
        while code_lines and not code_lines[0].strip():
            code_lines.pop(0)
        code = "\n".join(code_lines)

        from evaluator import evaluate
        c_hash = short_hash(code)
        print(f"  [gen 0 slot 0] Evaluating seeded champion (hash {c_hash})...")
        result = evaluate(code)
        fitness_str = f"{result.fitness:.4f}" if result.fitness != float("inf") else "inf"
        print(f"  [gen 0 slot 0] Fitness: {fitness_str}  ({result.total_elapsed_s}s)")

        # Log it like any other candidate
        from datetime import datetime, timezone
        from dataclasses import asdict
        entry = {
            "timestamp":       datetime.now(timezone.utc).isoformat(),
            "generation":      0,
            "slot":            0,
            "parent_hash":     None,
            "model":           "seeded_from_file",
            "mode":            config.MODE,
            "prompt_hash":     "seeded",
            "code_hash":       c_hash,
            "code":            code,
            "fitness":         result.fitness if result.fitness != float("inf") else None,
            "all_succeeded":   result.all_succeeded,
            "per_instance":    [asdict(r) for r in result.per_instance],
            "llm_elapsed_s":   0.0,
            "total_elapsed_s": result.total_elapsed_s,
        }
        log_candidate(entry)
    else:
        seed_prompt = load_seed_prompt()
        code, result, c_hash = produce_and_evaluate(
            prompt=seed_prompt,
            generation=0,
            slot=0,
            parent_hash=None,
        )

    if result.fitness == float("inf"):
        print("\n[ERROR] Seed candidate failed. Cannot start evolution without a valid champion.")
        print("        Consider running driver.py a few times to get a valid seed candidate,")
        print("        or inspecting logs/candidates.jsonl for the error.")
        return

    champion_code = code
    champion_fitness = result.fitness
    champion_hash = c_hash

    log_generation({
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "generation":        0,
        "champion_hash":     champion_hash,
        "champion_fitness":  champion_fitness,
        "gen_best_hash":     champion_hash,
        "gen_best_fitness":  champion_fitness,
        "gen_worst_fitness": champion_fitness,
        "num_candidates":    1,
        "num_succeeded":     1,
    })

    print(f"\n[Generation 0 champion] hash={champion_hash}, fitness={champion_fitness:.4f}")

    stagnation_gens = 0   # generations since last champion improvement

    # ----- Generations 1..N: evolve or diversify prompt -----
    for gen in range(1, config.NUM_GENERATIONS + 1):
        print(f"\n{'='*70}\nGeneration {gen}\n{'='*70}")
        print(f"Current champion: {champion_hash}, fitness={champion_fitness:.4f}")

        if stagnation_gens >= config.STAGNATION_THRESHOLD:
            prompt = build_diversify_prompt(champion_code, champion_fitness, stagnation_gens)
            prompt_kind = "diversify"
        else:
            prompt = build_evolve_prompt(champion_code, champion_fitness)
            prompt_kind = "evolve"
        print(f"Prompt kind: {prompt_kind}  (stagnation: {stagnation_gens} gens)")

        gen_fitnesses: list[tuple[float, str, str]] = []  # (fitness, hash, code)
        num_succeeded = 0

        for slot in range(config.LAMBDA):
            code, result, c_hash = produce_and_evaluate(
                prompt=prompt,
                generation=gen,
                slot=slot,
                parent_hash=champion_hash,
            )
            if result.fitness != float("inf"):
                gen_fitnesses.append((result.fitness, c_hash, code))
                num_succeeded += 1

        # Selection: does anyone beat the current champion?
        if gen_fitnesses:
            gen_fitnesses.sort(key=lambda t: t[0])
            gen_best_fitness, gen_best_hash, gen_best_code = gen_fitnesses[0]
            gen_worst_fitness = gen_fitnesses[-1][0]

            if gen_best_fitness < champion_fitness:
                print(f"\n  NEW CHAMPION: {gen_best_hash}  fitness {gen_best_fitness:.4f}  "
                      f"(was {champion_fitness:.4f}, delta {gen_best_fitness - champion_fitness:+.4f})")
                champion_code = gen_best_code
                champion_fitness = gen_best_fitness
                champion_hash = gen_best_hash
                stagnation_gens = 0
            else:
                print(f"\n  Champion unchanged. Best of gen: {gen_best_hash} "
                      f"({gen_best_fitness:.4f} vs champion {champion_fitness:.4f})")
                stagnation_gens += 1
        else:
            gen_best_fitness = None
            gen_best_hash = None
            gen_worst_fitness = None
            stagnation_gens += 1
            print(f"\n  All {config.LAMBDA} candidates in generation {gen} failed. Champion unchanged.")

        log_generation({
            "timestamp":         datetime.now(timezone.utc).isoformat(),
            "generation":        gen,
            "prompt_kind":       prompt_kind,
            "stagnation_gens":   stagnation_gens,
            "champion_hash":     champion_hash,
            "champion_fitness":  champion_fitness,
            "gen_best_hash":     gen_best_hash,
            "gen_best_fitness":  gen_best_fitness,
            "gen_worst_fitness": gen_worst_fitness,
            "num_candidates":    config.LAMBDA,
            "num_succeeded":     num_succeeded,
        })

    # ----- Final summary -----
    print("\n" + "=" * 70)
    print("EVOLUTION COMPLETE")
    print("=" * 70)
    print(f"Final champion:  {champion_hash}")
    print(f"Final fitness:   {champion_fitness:.4f}")
    print(f"Interpretation:  {(1 - champion_fitness) * 100:+.2f}% vs random baseline")
    print(f"Logs: {config.CANDIDATES_LOG.name} + {config.GENERATIONS_LOG.name}")


if __name__ == "__main__":
    main()