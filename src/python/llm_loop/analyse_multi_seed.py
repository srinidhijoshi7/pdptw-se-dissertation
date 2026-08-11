"""
Analyse multi-seed evaluation results.

Reads results/multi_seed_evaluation.json (or falls back to
multi_seed_runs.jsonl if the run is still in progress) and produces:
  - Random baseline: raw cost mean & std per instance across seeds
  - Champion & tightest_tw: mean +/- std of ratio to SAME-SEED random baseline
    (critical: never mixes seeds across numerator and denominator)
  - Aggregate row: mean of means, mean of stds across instances
  - Win/loss/tie counts (based on per-instance mean ratio vs 1.0)

Writes results/champions_multi_seed_summary.md and prints it to stdout.

Run from src/python/llm_loop/:
    python analyse_multi_seed.py
"""
import json
import statistics

import config


RESULTS_DIR = config.LLM_LOOP_DIR / "results"
RUNS_JSONL = RESULTS_DIR / "multi_seed_runs.jsonl"
FINAL_JSON = RESULTS_DIR / "multi_seed_evaluation.json"
SUMMARY_MD = RESULTS_DIR / "champions_multi_seed_summary.md"


def load_runs() -> tuple[list[dict], dict]:
    if FINAL_JSON.exists():
        obj = json.loads(FINAL_JSON.read_text())
        return obj["runs"], obj.get("meta", {})
    if RUNS_JSONL.exists():
        runs = []
        with RUNS_JSONL.open() as f:
            for line in f:
                line = line.strip()
                if line:
                    runs.append(json.loads(line))
        return runs, {}
    raise SystemExit(f"No results found: {FINAL_JSON} or {RUNS_JSONL}")


def mean_std(values: list[float]) -> tuple[float, float, int]:
    if not values:
        return (float("nan"), float("nan"), 0)
    n = len(values)
    m = statistics.mean(values)
    s = statistics.stdev(values) if n > 1 else 0.0
    return (m, s, n)


def main() -> None:
    runs, meta = load_runs()
    print(f"Loaded {len(runs)} runs.\n")

    seeds = sorted({r["seed"] for r in runs})
    instances = list(config.INSTANCE_GRID_FULL)
    for inst in sorted({r["instance"] for r in runs}):
        if inst not in instances:
            instances.append(inst)
    champions = sorted({r["tag"] for r in runs if r["kind"] == "champion"})

    # Index random baselines by (seed, instance)
    random_cost: dict[tuple[int, str], float] = {}
    for r in runs:
        if r["kind"] == "baseline" and r["tag"] == "random" and r["cost"] is not None:
            random_cost[(r["seed"], r["instance"])] = r["cost"]

    # Collect costs per (tag, instance) with seed
    champ_costs: dict[tuple[str, str], list[tuple[int, float]]] = {}
    for r in runs:
        if r["kind"] == "champion" and r["cost"] is not None:
            champ_costs.setdefault((r["tag"], r["instance"]), []).append((r["seed"], r["cost"]))

    tw_costs: dict[str, list[tuple[int, float]]] = {}
    for r in runs:
        if r["kind"] == "baseline" and r["tag"] == "tightest_tw" and r["cost"] is not None:
            tw_costs.setdefault(r["instance"], []).append((r["seed"], r["cost"]))

    have_tw = bool(tw_costs)

    def ratio_stats(pairs: list[tuple[int, float]], instance: str) -> tuple[float, float, int]:
        """Ratio to SAME-SEED random baseline for this instance."""
        ratios = []
        for seed, cost in pairs:
            base = random_cost.get((seed, instance))
            if base and base > 0:
                ratios.append(cost / base)
        return mean_std(ratios)

    # ---- Report ----
    lines: list[str] = []
    lines.append("# Multi-Seed Variance Evaluation Summary\n")
    lines.append(f"- Seeds: `{seeds}`")
    lines.append(f"- Instances: {len(instances)}")
    lines.append(f"- Champions: `{champions}`")
    lines.append(f"- Baselines evaluated at each seed: `random`" + (", `tightest_tw`" if have_tw else ""))
    if meta:
        lines.append(f"- `--mslpa`: {meta.get('mslpa')}, `--max_time`: {meta.get('max_time')}s")
        if meta.get("started_at"):
            lines.append(f"- Started: {meta['started_at']}")
        if meta.get("finished_at"):
            lines.append(f"- Finished: {meta['finished_at']}")
    lines.append("")
    lines.append("Ratios below are computed against the **same-seed** random baseline. "
                 "A value < 1.000 means the candidate beats random on average across seeds.\n")

    # Random baseline raw cost table
    lines.append("## Random baseline cost across seeds\n")
    lines.append("| Instance | Mean cost | Std | n |")
    lines.append("|---|---|---|---|")
    for inst in instances:
        costs = [c for (s, c) in
                 [(r["seed"], r["cost"]) for r in runs
                  if r["kind"] == "baseline" and r["tag"] == "random"
                  and r["instance"] == inst and r["cost"] is not None]]
        m, s, n = mean_std(costs)
        lines.append(f"| {inst} | {m:.2f} | {s:.2f} | {n} |")
    lines.append("")

    # Champion & tightest_tw ratios
    lines.append("## Champion ratios to same-seed random baseline\n")
    lines.append("Format: `mean ± std (n)`.\n")

    header = ["Instance"]
    if have_tw:
        header.append("tightest_tw")
    header += list(champions)

    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")

    col_means: dict[str, list[float]] = {c: [] for c in header[1:]}
    col_stds:  dict[str, list[float]] = {c: [] for c in header[1:]}

    for inst in instances:
        row = [inst]
        if have_tw:
            m, s, n = ratio_stats(tw_costs.get(inst, []), inst)
            row.append(f"{m:.4f} ± {s:.4f} ({n})" if n else "—")
            if n:
                col_means["tightest_tw"].append(m)
                col_stds["tightest_tw"].append(s)
        for champ in champions:
            m, s, n = ratio_stats(champ_costs.get((champ, inst), []), inst)
            row.append(f"{m:.4f} ± {s:.4f} ({n})" if n else "—")
            if n:
                col_means[champ].append(m)
                col_stds[champ].append(s)
        lines.append("| " + " | ".join(row) + " |")

    # Aggregate
    agg = ["**Mean across instances**"]
    for c in header[1:]:
        if col_means[c]:
            agg.append(f"**{statistics.mean(col_means[c]):.4f} ± {statistics.mean(col_stds[c]):.4f}**")
        else:
            agg.append("**—**")
    lines.append("| " + " | ".join(agg) + " |")
    lines.append("")

    # Wins / losses / ties
    lines.append("## Wins, losses, ties (per-instance mean ratio vs 1.0)\n")
    lines.append("Win: mean ratio < 0.999 (beats random). Loss: > 1.001. Tie: within ±0.001.\n")
    lines.append("| Candidate | Wins | Losses | Ties |")
    lines.append("|---|---|---|---|")

    def wlt_champ(champ: str) -> tuple[int, int, int]:
        w = l = t = 0
        for inst in instances:
            m, _, n = ratio_stats(champ_costs.get((champ, inst), []), inst)
            if not n:
                continue
            if m < 0.999:
                w += 1
            elif m > 1.001:
                l += 1
            else:
                t += 1
        return (w, l, t)

    def wlt_tw() -> tuple[int, int, int]:
        w = l = t = 0
        for inst in instances:
            m, _, n = ratio_stats(tw_costs.get(inst, []), inst)
            if not n:
                continue
            if m < 0.999:
                w += 1
            elif m > 1.001:
                l += 1
            else:
                t += 1
        return (w, l, t)

    if have_tw:
        w, l, t = wlt_tw()
        lines.append(f"| tightest_tw | {w} | {l} | {t} |")
    for champ in champions:
        w, l, t = wlt_champ(champ)
        lines.append(f"| {champ} | {w} | {l} | {t} |")
    lines.append("")

    # Per-instance per-seed detail
    lines.append("## Per-seed detail (appendix)\n")
    for inst in instances:
        lines.append(f"### {inst}\n")
        header2 = ["Seed", "random (cost)"]
        if have_tw:
            header2.append("tightest_tw (ratio)")
        header2 += [f"{c} (ratio)" for c in champions]
        lines.append("| " + " | ".join(header2) + " |")
        lines.append("|" + "|".join(["---"] * len(header2)) + "|")
        for seed in seeds:
            base = random_cost.get((seed, inst))
            row = [str(seed), f"{base:.2f}" if base else "—"]
            if have_tw:
                pair = next(((s, c) for (s, c) in tw_costs.get(inst, []) if s == seed), None)
                if pair and base:
                    row.append(f"{pair[1]/base:.4f}")
                else:
                    row.append("—")
            for champ in champions:
                pair = next(((s, c) for (s, c) in champ_costs.get((champ, inst), []) if s == seed), None)
                if pair and base:
                    row.append(f"{pair[1]/base:.4f}")
                else:
                    row.append("—")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    # Failures
    fails = [r for r in runs if r["cost"] is None]
    if fails:
        lines.append(f"## Failed runs ({len(fails)})\n")
        lines.append("| Kind | Tag | Instance | Seed | Exit | Timeout |")
        lines.append("|---|---|---|---|---|---|")
        for r in fails:
            lines.append(f"| {r['kind']} | {r['tag']} | {r['instance']} | {r['seed']} | "
                         f"{r['exit_code']} | {r.get('timeout', False)} |")
        lines.append("")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_MD.write_text("\n".join(lines))
    print("\n".join(lines))
    print(f"\nWrote {SUMMARY_MD}")


if __name__ == "__main__":
    main()