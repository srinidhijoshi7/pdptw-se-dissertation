"""
Figure 4.2: Per-instance multi-seed mean ratios for the three champions.

Data hardcoded from src/python/llm_loop/results/champions_multi_seed_summary.md.
Grouped bar chart with error bars (mean ± 1 std across 5 seeds), horizontal
parity line at 1.0.

Saves output to writing/figures/fig4_2_per_instance.png.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# From champions_multi_seed_summary.md
INSTANCES = ["lr101-6R", "lr102-6R", "lr103-6R", "lr201-6R", "lr101-10R", "lr102-10R"]
DATA = {
    "Gen 1": {
        "mean": [1.0011, 1.0011, 1.0287, 1.0200, 0.9814, 1.0068],
        "std":  [0.0019, 0.0024, 0.0375, 0.0201, 0.0831, 0.0143],
    },
    "Gen 2": {
        "mean": [0.9994, 1.0000, 1.0198, 0.9930, 1.0065, 1.0163],
        "std":  [0.0014, 0.0000, 0.0145, 0.0082, 0.0496, 0.0117],
    },
    "Gen 3": {
        "mean": [1.0024, 1.0021, 0.9943, 0.9960, 1.0025, 1.0173],
        "std":  [0.0014, 0.0029, 0.0121, 0.0089, 0.0993, 0.0126],
    },
}
COLOURS = {"Gen 1": "#1f77b4", "Gen 2": "#ff7f0e", "Gen 3": "#d62728"}

x = np.arange(len(INSTANCES))
width = 0.27

fig, ax = plt.subplots(figsize=(11, 5.5))

for i, (label, d) in enumerate(DATA.items()):
    offset = (i - 1) * width
    means = np.array(d["mean"])
    stds = np.array(d["std"])
    ax.bar(x + offset, means, width, yerr=stds, label=label,
           color=COLOURS[label], edgecolor="white", linewidth=0.8,
           capsize=3, error_kw={"linewidth": 0.8, "alpha": 0.7})

# Parity line
ax.axhline(1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.6, zorder=1)
ax.text(len(INSTANCES) - 0.5, 1.0, "  parity with random",
        va="center", fontsize=8, color="#333333")

ax.set_xlabel("Instance", fontsize=11)
ax.set_ylabel("Mean ratio to same-seed random baseline (± 1 std, n=5)", fontsize=11)
ax.set_xticks(x)
ax.set_xticklabels(INSTANCES)
ax.legend(loc="upper left", fontsize=10, framealpha=0.9)
ax.grid(True, axis="y", alpha=0.3)
ax.set_axisbelow(True)
ax.set_ylim(0.92, 1.08)

plt.tight_layout()
out = REPO_ROOT / "writing/figures/fig4_2_per_instance.png"
plt.savefig(out, dpi=300, bbox_inches="tight")
print(f"Saved: {out}")