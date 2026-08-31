# Dissertation code handoff — Srinidhi Joshi

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
