"""
Multi-seed variance evaluation for the three champions and baselines.

Runs (baselines + 3 champions) x 6 instances x 5 seeds = 150 MSLP calls at
--mslpa=10. Writes each result to results/multi_seed_runs.jsonl as it
completes (idempotent — safe to Ctrl-C and rerun). On successful completion
consolidates to results/multi_seed_evaluation.json.

No LLM/Gemini usage. Pure Julia subprocess calls.

Run from src/python/llm_loop/:
    python multi_seed_eval.py
"""
import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone

import config


# ============================================================
# Experiment configuration
# (independent of config.SEED / config.INSTANCE_GRID so that changing
#  the evolution driver's settings can't accidentally corrupt these runs)
# ============================================================
SEEDS = [17, 42, 100, 200, 500]

INSTANCES = config.INSTANCE_GRID_FULL  # all 6 instances

CHAMPIONS = [
    ("Gen1_d1791ed1796e", "first_beat_random_d1791ed1796e.jl"),
    ("Gen2_cbbe47d2468c", "gen2_cbbe47d2468c.jl"),
    ("Gen3_dacd3ec6f6c7", "gen3_dacd3ec6f6c7.jl"),
]

BASELINE_ORDERS = ["random", "tightest_tw"]

MSLPA = 10
MAX_TIME = 60
ALPHA = 0.05
JULIA_TIMEOUT = 180

RESULTS_DIR = config.LLM_LOOP_DIR / "results"
RUNS_JSONL = RESULTS_DIR / "multi_seed_runs.jsonl"
FINAL_JSON = RESULTS_DIR / "multi_seed_evaluation.json"

CANDIDATE_FILE = config.CANDIDATE_FILE  # Julia reads this via LLM_CANDIDATE_FILE env var


# ============================================================
# Helpers
# ============================================================
def strip_metadata_header(code: str) -> str:
    """Same logic as driver.py: strip leading '#' comment lines and blank lines."""
    lines = code.splitlines()
    while lines and lines[0].strip().startswith("#"):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines)


def parse_best_cost(stdout: str) -> float | None:
    m = re.search(r"Best solution value:\s*([\d.]+)", stdout)
    return float(m.group(1)) if m else None


def run_mslp(service_order: str, seed: int, instance_rel: str) -> dict:
    """
    Run a single MSLP call. If service_order is 'llm_candidate', the current
    contents of CANDIDATE_FILE are used — caller is responsible for writing
    the right champion code there first.
    """
    full_inst = config.INSTANCE_BASE_PATH + instance_rel
    cmd = [
        "julia", "pdptwse.jl",
        "--inst_path", full_inst,
        "--cut_off_machs", "4",
        "--method_type", "heur",
        "--method_code", "mslp",
        "--seed", str(seed),
        "--greedy_service_order", service_order,
        "--alpha", str(ALPHA),
        "--threads", "1",
        "--output_flag_grb_MSLP", "0",
        "--mslpa", str(MSLPA),
        "--mslpr", "I",
        "--max_time", str(MAX_TIME),
        "--output", "./logs/",
        "--print_sol", "0",
        "--solver_method", "A",
    ]
    env = os.environ.copy()
    env["LLM_CANDIDATE_FILE"] = str(CANDIDATE_FILE)

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=config.JULIA_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=JULIA_TIMEOUT,
        )
        return {
            "cost": parse_best_cost(result.stdout),
            "exit_code": result.returncode,
            "elapsed_s": round(time.time() - t0, 2),
            "timeout": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "cost": None,
            "exit_code": -1,
            "elapsed_s": JULIA_TIMEOUT,
            "timeout": True,
        }


def load_completed() -> set:
    """Read runs JSONL; return set of (kind, tag, instance, seed) already done."""
    completed = set()
    if not RUNS_JSONL.exists():
        return completed
    with RUNS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            completed.add((e["kind"], e["tag"], e["instance"], e["seed"]))
    return completed


def append_run(entry: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with RUNS_JSONL.open("a") as f:
        f.write(json.dumps(entry) + "\n")


def write_champion_code(champion_file: str) -> None:
    """Load and strip a champion .jl file, write to the candidate file."""
    src = config.LLM_LOOP_DIR / "champions" / champion_file
    if not src.exists():
        raise FileNotFoundError(f"Champion file not found: {src}")
    code = strip_metadata_header(src.read_text())
    CANDIDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATE_FILE.write_text(code)


# ============================================================
# Main
# ============================================================
def main() -> None:
    total_runs = len(SEEDS) * len(INSTANCES) * (len(BASELINE_ORDERS) + len(CHAMPIONS))

    print("=" * 70)
    print("Multi-seed variance evaluation")
    print("=" * 70)
    print(f"Seeds:      {SEEDS}")
    print(f"Instances:  {len(INSTANCES)}")
    print(f"Champions:  {[c[0] for c in CHAMPIONS]}")
    print(f"Baselines:  {BASELINE_ORDERS}")
    print(f"Total runs: {total_runs}")
    print(f"--mslpa={MSLPA}, --max_time={MAX_TIME}, --alpha={ALPHA}")
    print(f"Output:     {RUNS_JSONL}")
    print("=" * 70)

    completed = load_completed()
    if completed:
        print(f"\nResuming: {len(completed)}/{total_runs} runs already completed; skipping those.")

    done = len(completed)
    started_at = datetime.now(timezone.utc).isoformat()

    for seed in SEEDS:
        print(f"\n{'='*70}\nSEED {seed}\n{'='*70}")

        # ---- Baselines ----
        for order in BASELINE_ORDERS:
            for instance in INSTANCES:
                key = ("baseline", order, instance, seed)
                if key in completed:
                    continue
                done += 1
                print(f"[{done}/{total_runs}] baseline={order} seed={seed} inst={instance}")
                r = run_mslp(order, seed, instance)
                append_run({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "kind": "baseline",
                    "tag": order,
                    "instance": instance,
                    "seed": seed,
                    **r,
                })
                completed.add(key)
                cost_str = f"{r['cost']:.2f}" if r["cost"] is not None else "FAIL"
                print(f"    -> cost {cost_str}  ({r['elapsed_s']}s)")

        # ---- Champions ----
        for champ_name, champ_file in CHAMPIONS:
            block_pending = [
                inst for inst in INSTANCES
                if ("champion", champ_name, inst, seed) not in completed
            ]
            if not block_pending:
                continue
            write_champion_code(champ_file)

            for instance in INSTANCES:
                key = ("champion", champ_name, instance, seed)
                if key in completed:
                    continue
                done += 1
                print(f"[{done}/{total_runs}] champion={champ_name} seed={seed} inst={instance}")
                r = run_mslp("llm_candidate", seed, instance)
                append_run({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "kind": "champion",
                    "tag": champ_name,
                    "instance": instance,
                    "seed": seed,
                    **r,
                })
                completed.add(key)
                cost_str = f"{r['cost']:.2f}" if r["cost"] is not None else "FAIL"
                print(f"    -> cost {cost_str}  ({r['elapsed_s']}s)")

    # ---- Consolidate ----
    print("\nConsolidating runs into final JSON...")
    runs = []
    with RUNS_JSONL.open() as f:
        for line in f:
            line = line.strip()
            if line:
                runs.append(json.loads(line))

    final = {
        "meta": {
            "seeds": SEEDS,
            "instances": INSTANCES,
            "champions": [c[0] for c in CHAMPIONS],
            "baseline_orders": BASELINE_ORDERS,
            "mslpa": MSLPA,
            "max_time": MAX_TIME,
            "alpha": ALPHA,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "total_runs": len(runs),
        },
        "runs": runs,
    }
    FINAL_JSON.write_text(json.dumps(final, indent=2))
    print(f"Wrote {FINAL_JSON}  ({len(runs)} runs).")
    print("\nNext: python analyse_multi_seed.py")


if __name__ == "__main__":
    main()