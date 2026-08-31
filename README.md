# LLM-Driven Insertion-Scoring Heuristics for the PDPTW-SE

**Authors:** Srinidhi Narasimha Joshi and Dr Sunil Tiwari
**Affiliation:** University of Bristol Business School
**Contact:** gt25634@bristol.ac.uk

A FunSearch-style evolutionary pipeline that uses a large language model to
discover insertion-scoring heuristics inside the Multi-Start LP-Improvement
(MSLP) framework for the Pickup and Delivery Problem with Time Windows and
Scheduling on the Edges (PDPTW-SE).

This repository accompanies an MSc Business Analytics dissertation submitted
to the University of Bristol in September 2026.

---

## Contribution summary

| Component | Source |
|---|---|
| PDPTW-SE formulation, MSLP heuristic, Julia base codebase | Barbosa, Tiwari and Melo (2026) |
| Multi-island (Type 1) benchmark instances and generators | Barbosa, Tiwari and Melo (2026) |
| LLM-driven (1+lambda) evolutionary loop | This work (Joshi and Tiwari) |
| Three-prompt cascade: seed, evolve, diversify | This work |
| Runtime Julia code-injection mechanism | This work |
| Same-seed ratio-based evaluation harness | This work |
| Three evolved champion scoring functions | This work |
| Multi-seed variance and plateau analysis | This work |

---

## Reproducing the central result (about 20 minutes)

Reproduces Chapter 4 of the dissertation: the three-champion comparison
against the `random` and `tightest_tw` baselines across the six-instance
multi-island Type 1 grid at seed 17. **No Python and no LLM API key needed.**

Prerequisites: Julia 1.11.3, Gurobi 12.x with an active licence (a free
academic WLS licence is sufficient), about 500 MB free disk.

```bash
git clone https://github.com/srinidhijoshi7/pdptw-se-dissertation.git
cd pdptw-se-dissertation

cd src/julia
julia --project=. -e "using Pkg; Pkg.instantiate()"
bash run_champions.sh
```

Expected output at seed 17, `--mslpa 10`, `--alpha 0.05`:

| Instance | random | Gen 1 | Gen 2 | Gen 3 |
|---|---|---|---|---|
| lr101-6R | 766.20 | 1.0000 | 0.9969 | 1.0000 |
| lr102-6R | 542.25 | 1.0053 | 1.0000 | 1.0000 |
| lr103-6R | 454.61 | 1.0335 | 1.0301 | 0.9989 |
| lr201-6R | 846.44 | 1.0000 | 0.9925 | 1.0000 |
| lr101-10R | 1297.54 | 0.9757 | 0.9681 | 0.9744 |
| lr102-10R | 1033.45 | 1.0000 | 1.0082 | 1.0082 |
| **Mean** | | **1.0024** | **0.9993** | **0.9969** |

Ratios are candidate cost divided by same-seed `random` cost; below 1.0 beats
random. Agreement to three decimal places confirms the injection mechanism is
deterministic across machines. Full instructions, including the optional live
evolution loop, are in [HANDOFF.md](HANDOFF.md) and Appendix F of the
dissertation.

---

## Where things live

| Path | Contents |
|---|---|
| `src/julia/run_champions.sh` | Central reproduction script |
| `src/julia/test_injection.sh` | A/B test showing injection is variance-neutral |
| `src/julia/modules/Multistart/src/heuristic/init_solution.jl` | The `get_service_order` dispatcher, the single injection point |
| `src/python/llm_loop/driver.py` | The (1+lambda = 2) evolutionary loop |
| `src/python/llm_loop/prompts/` | `seed.md`, `evolve.md`, `diversify.md` |
| `src/python/llm_loop/champions/` | The three evolved Julia champions |
| `src/python/llm_loop/results/` | Multi-seed and plateau-extension results |
| `src/python/llm_loop/logs/archive/` | Per-candidate and per-generation JSONL logs |
| `writing/` | Dissertation source in Markdown |
| `docs/BASE_README.md` | Original Barbosa, Tiwari and Melo documentation |

---

## Base work

The PDPTW-SE formulation, the MSLP heuristic, the Julia codebase and the
benchmark instance families extended here are from:

> Barbosa, V.A., Tiwari, S. and Melo, R.A. (2026) 'The pickup and delivery
> problem with time windows and scheduling on the edges', *European Journal
> of Operational Research*. https://doi.org/10.1016/j.ejor.2026.01.036

Base repository: https://github.com/ab-vitor/pdptw-se

Their original documentation is preserved unaltered at
[docs/BASE_README.md](docs/BASE_README.md), covering the Julia and Python code
layout, the MIP formulations, the instance generator and the R statistics
scripts.

---

## Software stack

Julia 1.11.3 (juliaup), Python 3.10.14 (pyenv), Gurobi 12.0.3 (WLS Academic),
JuMP 1.23.6, Gurobi.jl 1.5.0, Gurobi_jll 12.0.2, google-genai 2.16.0,
python-dotenv 1.2.2. Developed and verified on Apple Silicon (arm64, macOS 14).

---

## Citing

For the pipeline, champions and analysis in this repository:

> Joshi, S.N. and Tiwari, S. (2026) *Evolving Insertion-Scoring Heuristics
> with Large Language Models: A FunSearch-Style Approach to the PDPTW with
> Scheduling on Edges*. MSc dissertation, University of Bristol Business School.

For the underlying MSLP heuristic and PDPTW-SE formulation, cite Barbosa,
Tiwari and Melo (2026) above.

---

## Licence

MIT. See [LICENSE](LICENSE), which carries copyright notices for both the base
MSLP implementation and the additions made in this work.
