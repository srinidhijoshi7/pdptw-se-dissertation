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

The three champions and the two hand-designed baseline rules — `random` and
`tightest_tw`, both defined in §3.2 — were evaluated on the six-instance
multi-island (Type 1) grid at seed 17 with `--mslpa = 10`, `--alpha = 0.05`.
Table 4.1 reports the resulting costs and per-instance ratios of candidate
cost to the same-seed `random` baseline; ratios below 1.0 indicate the
candidate beat `random` on that instance, ratios above 1.0 indicate it lost,
and 1.000 indicates parity.

**Table 4.1.** Single-seed (seed 17) grid comparison at `--mslpa = 10`.
Absolute `random` cost is shown in the second column; the remaining columns
report ratios to that column, so lower is better. The best (lowest) ratio in
each row is bolded. Instance paths: `06R_06V_02I_04M/t1/` for `lr101-6R`,
`lr102-6R`, `lr103-6R`; `06R_06V_02I_04M/t2/` for `lr201-6R`;
`10R_10V_02I_04M/t1/` for `lr101-10R`, `lr102-10R`.

| Instance   | random (cost) | `tightest_tw` | Gen 1      | Gen 2       | Gen 3       |
|------------|---------------|---------------|------------|-------------|-------------|
| lr101-6R   | 766.20        | 1.0000        | 1.0000     | **0.9969**  | 1.0000      |
| lr102-6R   | 542.25        | 1.0053        | 1.0053     | **1.0000**  | **1.0000**  |
| lr103-6R   | 454.61        | 1.0176        | 1.0335     | 1.0301      | **0.9989**  |
| lr201-6R   | 846.44        | 1.0000        | 1.0000     | **0.9925**  | 1.0000      |
| lr101-10R  | 1297.54       | 0.9908        | 0.9757     | **0.9681**  | 0.9744      |
| lr102-10R  | 1033.45       | 1.0382        | **1.0000** | 1.0082      | 1.0082      |
| **Mean**   |               | 1.0087        | 1.0024     | 0.9993      | **0.9969**  |

Reading the table row by row, Gen 2 is the strict winner or joint winner on
five of the six instances at this seed, with a decisive win on `lr101-10R`
(the instance on which it was evolved). Gen 3 is the only champion that
beats `random` on `lr103-6R`, an instance on which Gen 1 and Gen 2 both
lose by 3.01–3.35%. `lr102-10R` is a persistent negative case for the two
grid-generalising champions (Gen 2 and Gen 3), which both lose 0.82%;
only Gen 1 matches `random` on this instance, and only by tying it exactly.
The `tightest_tw` baseline is worse than or equal to `random` on every
instance except `lr101-10R`, where it produces a modest 0.92% improvement.

Aggregating across the six instances, mean ratios improve monotonically
across the three champions: 1.0024 (Gen 1) → 0.9993 (Gen 2) → 0.9969
(Gen 3). All three LLM-evolved champions produce a lower mean ratio than
the `tightest_tw` baseline (1.0087), and Gen 2 and Gen 3 produce a lower
mean ratio than `random` (1.0000). This picture — a single seed on a fixed
grid — is the starting point for §4.4, which extends the evaluation across
five seeds to test whether the seed-17 result is representative of the
champions' behaviour under seed variation.

## 4.4 Multi-seed variance analysis

*[Section to follow.]*

## 4.5 Per-instance analysis

*[Section to follow.]*

## 4.6 Structural characteristics of the three champions

*[Section to follow.]*

## 4.7 Evolutionary plateau (generations 9–16)

*[Section to follow.]*