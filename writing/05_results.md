# Chapter 4 — Findings

*[Target: ~2500 words.]*

## 4.1 Chapter roadmap

*[To be written last, after §§4.2–4.7 exist.]*

## 4.2 Champion progression

Gen 1 (`d1791ed1796e`) was the first LLM-generated candidate in this
dissertation's experimental record to achieve a fitness value below 1.0000.
It was produced in an initial evolutionary run seeded from the seed prompt
(§3.6), with no champion-seed file present, running in dev mode on the
`10R_10V_02I_04M/t1/lr101` instance at seed 17, λ = 2, and `--mslpa = 10`.
On its training instance, Gen 1 achieved a candidate cost of 1265.95
against a random baseline of 1297.54, giving a fitness of 0.9757 — an
improvement of 2.43% over the same-seed random rule. The candidate emerged
at generation 1, slot 0, from the evolve prompt. It is archived at
`src/python/llm_loop/champions/first_beat_random_d1791ed1796e.jl` with
provenance metadata; its structural characterisation is deferred to §4.6.

Gen 2 (`cbbe47d2468c`) was produced in a subsequent dev-mode session,
seeded from Gen 1 via the champion-seed mechanism (§3.5) rather than from
a fresh seed prompt. Configuration was otherwise identical to the Gen 1
run: dev mode on lr101-10R, seed 17, λ = 2, `--mslpa = 10`. On the same
training instance, Gen 2 reached a candidate cost of 1256.16, giving a
fitness of 0.9681 — a 3.19% improvement over random and a 0.76%
improvement over Gen 1. It emerged at generation 1, slot 1, from the
evolve prompt, not from diversify. It is archived at
`src/python/llm_loop/champions/gen2_cbbe47d2468c.jl`. One contextual point
matters for what follows: Gen 1 and Gen 2 were both optimised for a single
instance. Their behaviour on the six-instance grid is a separate question,
addressed in §4.3.

Gen 3 (`dacd3ec6f6c7`) was produced in a third session with the
evolutionary loop reconfigured to compute fitness as the mean ratio across
all six instances of the grid (MODE = full), rather than on the single
training instance used for Gen 1 and Gen 2. It was seeded from Gen 2 via
the champion-seed mechanism, with the remaining configuration held
constant: seed 17, λ = 2, `--mslpa = 10`. Gen 3 achieved a grid fitness of
0.9969, a 0.24% improvement over Gen 2 on the same metric. The
methodologically significant fact is that Gen 3 emerged at generation 3,
slot 0, from the **diversify** prompt — the first (and, across the sixteen
generations of full-grid evolution reported in §4.7, only) time the
diversify mechanism directly produced a winning champion. This followed
two consecutive stagnation generations under the evolve prompt. It is
archived at `src/python/llm_loop/champions/gen3_dacd3ec6f6c7.jl`. Together,
these three champions define the trajectory that §§4.3–4.7 unpack.

## 4.3 Grid comparison against baselines

*[Section to follow.]*

## 4.4 Multi-seed variance analysis

*[Section to follow.]*

## 4.5 Per-instance analysis

*[Section to follow.]*

## 4.6 Structural characteristics of the three champions

*[Section to follow.]*

## 4.7 Evolutionary plateau (generations 9–16)

*[Section to follow.]*