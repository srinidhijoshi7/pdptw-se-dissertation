"""
Figure 4.1: Fitness trajectory across sixteen generations of full-grid evolution.

Reads session-1 (Chat 06 gens 1-8) and session-2 (extension gens 9-16)
generation logs from src/python/llm_loop/logs/archive/. Uses the
prompt_kind field directly from each generation record.

Saves output to writing/figures/fig4_1_trajectory.png.
"""

import json
import matplotlib.pyplot as plt
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GEN3_FITNESS = 0.9969

SESSION1_GEN = REPO_ROOT / "src/python/llm_loop/logs/archive/generations_2026-08-10_full_gen1-8.jsonl"
SESSION2_GEN = REPO_ROOT / "src/python/llm_loop/logs/archive/generations_2026-08-11_gen9-16_extension.jsonl"


def load_jsonl(path):
    entries = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def build_gen_records(gen_path, gen_offset=0):
    """
    Extract (display_gen_number, gen_best_fitness, prompt_kind) from a
    generations log. Skips gen 0 (the seeded champion).
    """
    records = []
    for g in load_jsonl(gen_path):
        if g["generation"] == 0:
            continue
        prompt = g.get("prompt_kind", "unknown")
        records.append((g["generation"] + gen_offset, g["gen_best_fitness"], prompt))
    return records


# Collect all 16 generations
records = []
records += build_gen_records(SESSION1_GEN, gen_offset=0)
records += build_gen_records(SESSION2_GEN, gen_offset=8)

print(f"Loaded {len(records)} generation records:")
for r in records:
    print(f"  Gen {r[0]:2d}: fitness={r[1]:.4f}, prompt={r[2]}")

# Plot
fig, ax = plt.subplots(figsize=(10, 5))

# Connecting line for trajectory
all_pts = sorted(records, key=lambda r: r[0])
ax.plot([p[0] for p in all_pts], [p[1] for p in all_pts],
        color="#666666", linewidth=0.8, alpha=0.4, zorder=1)

# Scatter by prompt type
marker_style = {
    "evolve":    {"marker": "o", "color": "#1f77b4", "label": "evolve prompt", "s": 80},
    "diversify": {"marker": "^", "color": "#d62728", "label": "diversify prompt", "s": 110},
    "seed":      {"marker": "s", "color": "#2ca02c", "label": "seed prompt", "s": 80},
    "unknown":   {"marker": "D", "color": "#999999", "label": "unknown", "s": 70},
}

by_prompt = {}
for gen, fit, prompt in records:
    by_prompt.setdefault(prompt, []).append((gen, fit))

for prompt in ["evolve", "diversify", "seed", "unknown"]:
    points = by_prompt.get(prompt, [])
    if not points:
        continue
    style = marker_style[prompt]
    ax.scatter([p[0] for p in points], [p[1] for p in points],
               marker=style["marker"], s=style["s"], color=style["color"],
               label=style["label"], zorder=3, edgecolors="white", linewidth=1)

# Gen 3 reference line
ax.axhline(GEN3_FITNESS, color="#d62728", linestyle="--", linewidth=1,
           alpha=0.7, zorder=2)
ax.text(16.3, GEN3_FITNESS, f"  Gen 3\n  {GEN3_FITNESS:.4f}",
        color="#d62728", va="center", fontsize=9)

# Session boundary
ax.axvline(8.5, color="#999999", linestyle=":", linewidth=1, alpha=0.6)

# Session labels
y_range = ax.get_ylim()
label_y = y_range[1] - (y_range[1] - y_range[0]) * 0.03
ax.text(4.5, label_y, "Session 1 (gens 1–8)",
        ha="center", fontsize=9, color="#666666")
ax.text(12.5, label_y, "Session 2 (gens 9–16, extension)",
        ha="center", fontsize=9, color="#666666")

ax.set_xlabel("Generation", fontsize=11)
ax.set_ylabel("Best-of-generation fitness (mean ratio to random)", fontsize=11)
ax.set_xticks(range(1, 17))
ax.legend(loc="lower right", fontsize=9, framealpha=0.9)
ax.grid(True, alpha=0.3)

plt.tight_layout()
out = REPO_ROOT / "writing/figures/fig4_1_trajectory.png"
plt.savefig(out, dpi=300, bbox_inches="tight")
print(f"\nSaved: {out}")