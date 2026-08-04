"""
Candidate evaluation: run MSLP on each instance in the grid, compute fitness.

Fitness = mean over instances of (candidate_cost / baseline_random_cost).
Lower = better. 1.0 = matches random baseline. <1.0 = beats random.
Failed runs on any instance = infinite fitness (candidate discarded).
"""
import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field

import config


@dataclass
class InstanceResult:
    instance: str
    cost: float | None       # None if MSLP failed
    exit_code: int
    elapsed_s: float
    ratio: float | None      # cost / baseline; None if cost is None


@dataclass
class EvaluationResult:
    fitness: float           # inf if any instance failed
    per_instance: list[InstanceResult] = field(default_factory=list)
    total_elapsed_s: float = 0.0
    all_succeeded: bool = True


def load_baselines() -> dict[str, float]:
    if not config.BASELINES_FILE.exists():
        raise FileNotFoundError(f"Baselines not found: {config.BASELINES_FILE}")
    return json.loads(config.BASELINES_FILE.read_text())


def write_candidate(code: str) -> None:
    """Write candidate Julia code to the file Julia will include."""
    config.CANDIDATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.CANDIDATE_FILE.write_text(code)


def parse_best_cost(stdout: str) -> float | None:
    m = re.search(r"Best solution value:\s*([\d.]+)", stdout)
    return float(m.group(1)) if m else None


def run_mslp_on_instance(instance_rel: str) -> InstanceResult:
    """
    Run MSLP with the current candidate on one instance.
    Uses config.SEED, config.MAX_TIME, etc.
    """
    full_inst_path = config.INSTANCE_BASE_PATH + instance_rel

    cmd = [
        "julia", "pdptwse.jl",
        "--inst_path", full_inst_path,
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

    t0 = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=config.JULIA_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=config.JULIA_TIMEOUT,
        )
        elapsed = time.time() - t0
        cost = parse_best_cost(result.stdout)
        return InstanceResult(
            instance=instance_rel,
            cost=cost,
            exit_code=result.returncode,
            elapsed_s=round(elapsed, 2),
            ratio=None,   # filled in by evaluate()
        )
    except subprocess.TimeoutExpired:
        return InstanceResult(
            instance=instance_rel,
            cost=None,
            exit_code=-1,
            elapsed_s=config.JULIA_TIMEOUT,
            ratio=None,
        )


def evaluate(code: str) -> EvaluationResult:
    """
    Write candidate, run on all instances in config.INSTANCE_GRID,
    compute fitness = mean of cost/baseline ratios.
    """
    write_candidate(code)
    baselines = load_baselines()

    result = EvaluationResult(fitness=float("inf"))
    ratios: list[float] = []
    t_total = time.time()

    for inst_rel in config.INSTANCE_GRID:
        r = run_mslp_on_instance(inst_rel)

        if r.cost is None:
            r.ratio = None
            result.all_succeeded = False
        else:
            baseline = baselines.get(inst_rel)
            if baseline is None:
                # No baseline available; skip this instance's contribution
                r.ratio = None
            else:
                r.ratio = r.cost / baseline
                ratios.append(r.ratio)

        result.per_instance.append(r)

    result.total_elapsed_s = round(time.time() - t_total, 2)

    if result.all_succeeded and ratios:
        result.fitness = sum(ratios) / len(ratios)
    else:
        result.fitness = float("inf")

    return result