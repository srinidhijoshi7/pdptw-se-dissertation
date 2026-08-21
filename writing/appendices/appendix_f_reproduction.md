# Appendix F — Reproduction Instructions

This appendix reproduces the reproduction handoff document
(`HANDOFF.md`) that accompanies the project's source code in the
private Git repository. Section 3.7 of the main body describes the
reproducibility artefacts at the level of what exists and where; this
appendix supplies the operational detail — the exact commands, the
expected wall time, the expected numerical outputs, and the file-level
map of what code lives where. A reader with Julia 1.11.3 and Gurobi
12.x installed can follow these instructions on a fresh clone of the
repository and regenerate the central Chapter 4 comparison (Table 4.1
and the seed-17 columns of Table 4.2) in approximately twenty minutes,
without setting up Python, without a Gemini API key, and without
running the evolutionary loop itself.

The handoff document was originally authored to give the supervisor
independent verification of the dissertation's numerical claims. It is
reproduced here verbatim; the only modification is that the placeholder
GitHub handle `<yourhandle>` in the original document has been left as
`<yourhandle>` in this appendix, since the repository is private and
the actual URL is shared through non-public channels.

## F.1 Handoff document

**Source file:** `HANDOFF.md` (repository root)

---

# Dissertation code handoff — Srinidhi Joshi

Dear Sunil,

This is the code for my MSc dissertation, which extends your MSLP heuristic
with LLM-generated `get_service_order` candidates. The instructions below
let you reproduce the central Chapter 4 result — the three-champion
comparison against `random` and `tightest_tw` baselines on the six-instance
multi-island (Type 1) grid — without setting up Python or an LLM API key.

**Total time from clone to reproduction: ~20 minutes.**

## What's needed on your machine

- Julia 1.11.3 (matches the version in your original paper)
- Gurobi 12.x with an active licence
- Roughly 500 MB of disk

Everything else is in this repository.

## Setup

```bash
git clone https://github.com/<yourhandle>/pdptw-se-dissertation.git
cd pdptw-se-dissertation
git checkout srinidhi-dissertation

# Instantiate the Julia environment (one-time, ~5 minutes)
cd src/julia
julia --project=. -e "using Pkg; Pkg.instantiate()"
```

## Reproducing the three-champion comparison

Still in `src/julia/`:

```bash
bash run_champions.sh
```

This runs MSLP five times on each of the six instances:

- `random` baseline (your service-order rule)
- `tightest_tw` baseline (your service-order rule)
- Gen 1 champion (`d1791ed1796e`)
- Gen 2 champion (`cbbe47d2468c`)
- Gen 3 champion (`dacd3ec6f6c7`)

All at seed 17, `--mslpa=10`, `--alpha=0.05` — the exact protocol described
in Chapter 3 of the dissertation.

Progress prints to the terminal as each configuration finishes.
Individual outputs are saved to `src/julia/logs/handoff_reproduction/`.

## What you should see

Expected costs on my machine (seed 17):

| Instance   | random  | Gen 1 (ratio) | Gen 2 (ratio) | Gen 3 (ratio) |
|------------|---------|---------------|---------------|---------------|
| lr101-6R   | 766.20  | 1.0000        | 0.9969        | 1.0000        |
| lr102-6R   | 542.25  | 1.0053        | 1.0000        | 1.0000        |
| lr103-6R   | 454.61  | 1.0335        | 1.0301        | **0.9989**    |
| lr201-6R   | 846.44  | 1.0000        | 0.9925        | 1.0000        |
| lr101-10R  | 1297.54 | 0.9757        | 0.9681        | 0.9744        |
| lr102-10R  | 1033.45 | 1.0000        | 1.0082        | 1.0082        |
| **Mean**   |         | **1.0024**    | **0.9993**    | **0.9969**    |

If your numbers agree with these to three decimal places on all instances,
the injection mechanism is deterministic across machines and Chapter 4's
results are reproducible on your hardware.

Note the two persistent findings: Gen 3 is the only champion that beats
`random` on lr103-6R (the "lr103 breakthrough" discussed in Chapter 5),
and no champion beats `random` on lr102-10R (the "lr102-10R persistent
negative", also discussed in Chapter 5 as a limitation).

## Where the interesting code lives

- **Injection point:** `src/julia/modules/Multistart/src/heuristic/init_solution.jl`
  — search for `llm_candidate` to see the branch I added to `get_service_order`,
  the `LLM_CANDIDATE_FILE` env var loading, the module-level cache,
  and the `Base.invokelatest` wrapper for the world-age barrier.
- **Champion Julia functions:** `src/python/llm_loop/champions/`
  — the three LLM-generated scoring functions that the reproduction runs.
  Each file has a metadata header noting its generation, fitness, and lineage.
- **Python evolution driver:** `src/python/llm_loop/driver.py`
  — the 1+λ loop that produced the candidates. Not needed to reproduce
  Chapter 4's numbers, but this is where the seed/evolve/diversify prompt
  cascade lives.
- **Prompt templates:** `src/python/llm_loop/prompts/`
  — the three prompts described in Chapter 3 (seed.md, evolve.md, diversify.md).

## Optional: running the full evolutionary loop

If you'd like to see a new generation being produced live, there's a
second phase requiring Python, a Gemini API key (free tier), and ~20
minutes of runtime. This is not needed to verify Chapter 4's results.
Instructions are in `src/python/llm_loop/README.md`.

## Contact

Any issue at all — WhatsApp me and I'll debug live.

Srinidhi

---

## F.2 Repository structure summary

For reference, the top-level layout of the project repository is as
follows. The paths referenced throughout the dissertation resolve
against this structure.

```
pdptw-se-dissertation/
├── HANDOFF.md                              (reproduced in F.1 above)
├── writing/                                (Markdown source of this dissertation)
│   ├── 01_abstract.md
│   ├── 02_introduction.md
│   ├── 03_literature_review.md
│   ├── 04_methodology.md
│   ├── 05_results.md
│   ├── 06_discussion.md
│   ├── 07_conclusion.md
│   ├── references.md
│   ├── figures/                            (Figures 3.1, 4.1, 4.2 sources)
│   └── appendices/                         (Appendices A–F, this document)
├── src/
│   ├── julia/
│   │   ├── run_champions.sh                (Chapter 4 reproduction, ~20 min)
│   │   ├── test_injection.sh               (§3.3 A/B injection test)
│   │   └── modules/Multistart/src/heuristic/init_solution.jl
│   │                                       (get_service_order dispatcher, §3.3)
│   └── python/llm_loop/
│       ├── champions/                      (reproduced in Appendix C)
│       │   ├── first_beat_random_d1791ed1796e.jl
│       │   ├── gen2_cbbe47d2468c.jl
│       │   └── gen3_dacd3ec6f6c7.jl
│       ├── prompts/                        (reproduced in Appendix B)
│       │   ├── seed.md
│       │   ├── evolve.md
│       │   └── diversify.md
│       ├── driver.py                       ((1+λ) loop, §3.5)
│       ├── multi_seed_eval.py              (harness for multi-seed evaluation, §3.4)
│       ├── analyse_multi_seed.py           (aggregation into Table 4.2)
│       ├── results/
│       │   ├── multi_seed_evaluation.json  (Appendix D source)
│       │   ├── multi_seed_runs.jsonl
│       │   ├── champions_multi_seed_summary.md
│       │   └── gen9_16_plateau_extension.md
│       │                                   (Appendix E source)
│       └── logs/archive/
│           ├── candidates_2026-08-10_full_gen1-8.jsonl
│           ├── candidates_2026-08-11_gen9-16_extension.jsonl
│           ├── generations_2026-08-10_full_gen1-8.jsonl
│           └── generations_2026-08-11_gen9-16_extension.jsonl
│                                           (Appendix E source)
└── (other paths omitted for brevity)
```

## F.3 Cross-machine verification

The Chapter 4 reproduction described in F.1 has been verified once on
a second physical machine of matching architecture (Apple Silicon
arm64, macOS 14) on 18 August 2026, producing outputs identical to
three decimal places on all six instances. Reproducibility on non-Apple-
Silicon architectures (x86-64 Linux, x86-64 macOS, Windows-under-WSL)
has not been verified but is expected to hold to the same precision,
since the injection mechanism (Section 3.3) is architecture-neutral and
the underlying MSLP heuristic and Gurobi solver are cross-platform.
Any observed divergence beyond floating-point tolerance would indicate
either a Julia version mismatch (this study fixed 1.11.3), a Gurobi
version mismatch (this study fixed 12.0.3), or a change to the
injection code itself; the first two are checkable via `julia --version`
and `Gurobi.jl` version output, and the third via `git diff` against
the `srinidhi-dissertation` branch head.