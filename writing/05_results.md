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

The three champions and the two baseline rules were re-evaluated on the same
six-instance grid at five seeds — {17, 42, 100, 200, 500} — with all other
parameters (`--mslpa = 10`, `--alpha = 0.05`, `--max_time = 60`, `--threads = 1`)
held constant. `random` baseline costs were recomputed at each seed and used
as the denominator for the same-seed ratios reported in Table 4.2; every
ratio in the table shares its numerator and denominator seed. The run
comprised 90 champion evaluations plus 30 baseline evaluations, all completed
without failure.

**Table 4.2.** Multi-seed evaluation on the six-instance grid across seeds
{17, 42, 100, 200, 500}. Cells report the mean and standard deviation of the
per-seed ratio to the same-seed `random` baseline (n = 5); lower is better.
The best (lowest) mean ratio in each row is bolded.

| Instance   | `tightest_tw`         | Gen 1                 | Gen 2                 | Gen 3                     |
|------------|-----------------------|-----------------------|-----------------------|---------------------------|
| lr101-6R   | 1.0024 ± 0.0014       | 1.0011 ± 0.0019       | **0.9994 ± 0.0014**   | 1.0024 ± 0.0014           |
| lr102-6R   | 1.0053 ± 0.0000       | 1.0011 ± 0.0024       | **1.0000 ± 0.0000**   | 1.0021 ± 0.0029           |
| lr103-6R   | 1.0163 ± 0.0122       | 1.0287 ± 0.0375       | 1.0198 ± 0.0145       | **0.9943 ± 0.0121**       |
| lr201-6R   | 0.9960 ± 0.0089       | 1.0200 ± 0.0201       | **0.9930 ± 0.0082**   | 0.9960 ± 0.0089           |
| lr101-10R  | 1.0123 ± 0.0714       | **0.9814 ± 0.0831**   | 1.0065 ± 0.0496       | 1.0025 ± 0.0993           |
| lr102-10R  | 1.0455 ± 0.0110       | **1.0068 ± 0.0143**   | 1.0163 ± 0.0117       | 1.0173 ± 0.0126           |
| **Mean**   | 1.0130 ± 0.0175       | 1.0065 ± 0.0265       | 1.0058 ± 0.0142       | **1.0024 ± 0.0229**       |

Two observations follow from the table. First, the monotonic mean-ratio
improvement across the three champions holds under multi-seed evaluation
— Gen 1 (1.0065) → Gen 2 (1.0058) → Gen 3 (1.0024) — and all three
champions produce a lower mean ratio than the `tightest_tw` baseline
(1.0130). Second, however, no champion produces a mean ratio below 1.0 on
the grid: at this seed range and instance grid, none of the three
champions beats the `random` baseline on average. The favourable
seed-17 picture reported in §4.3 (Gen 3 mean of 0.9969) is therefore a
single-seed slice; averaged across five seeds it moves upward to 1.0024,
above parity with `random`.

The per-instance picture is more differentiated. Gen 3 beats `random` on
`lr103-6R` across all five seeds (mean 0.9943, worst-case 1.0000), and on
`lr201-6R` in mean (0.9960), reproducing the seed-17 breakthrough on
`lr103-6R` under seed variation. `lr101-10R` shows large per-seed variance
for every candidate (standard deviations in the range 0.05–0.10), with
individual per-seed ratios ranging from 0.9005 (Gen 1 at seed 42) to
1.1095 (Gen 3 at seed 100), indicating that MSLP at `--mslpa = 10` on this
instance is highly seed-sensitive irrespective of the injected ordering.
`lr102-10R` remains a persistent negative case for the two grid-optimised
champions: Gen 2 and Gen 3 both lose 1.63–1.73% on average, and neither
finds a seed at which they beat `random` on this instance. What these
observations imply about the reach and limits of LLM-driven heuristic
evolution in this setting — and about the interaction between MSLP's
own seed-sensitivity and the discriminative signal available to the
evolutionary loop — is addressed in Chapter 5.

## 4.5 Per-instance analysis

`lr103-6R` is the only instance in the grid on which Gen 3 uniquely beats
`random`. At seed 17, Gen 1 and Gen 2 both lose 3.01–3.35% (Table 4.1),
their largest single-instance loss on the grid; Gen 3 turns this into a
0.11% win (0.9989). Under multi-seed evaluation this reversal is
preserved: Gen 3's mean ratio is 0.9943 ± 0.0121 across the five seeds
(Table 4.2), with the worst per-seed value at 1.0000 and the best at
0.9726 (seed 100). Gen 1 and Gen 2, in contrast, retain their negative
sign under multi-seed evaluation, at means of 1.0287 and 1.0198
respectively. The instance itself has the smallest absolute `random`
baseline cost in the grid (454.61 at seed 17) — the smallest problem
size (six requests) in the multi-island (Type 1) family of Barbosa,
Tiwari and Melo (2026). The distinguishing feature of the three
champions relative to this instance is their evolutionary regime: Gen 1
and Gen 2 were both evolved with fitness computed on a single instance
(`lr101-10R`) that is structurally unlike `lr103-6R`, while Gen 3 was
evolved with fitness computed as the mean ratio across all six instances,
including `lr103-6R` itself. The mechanism by which this training-set
difference produces the observed structural rebalancing is developed in
Chapter 5.

`lr102-10R` is the sole instance in the grid on which no champion beats
`random`, at any seed. At seed 17, Gen 1 ties `random` (1.0000), and
Gen 2 and Gen 3 both lose 0.82% (Table 4.1). Under multi-seed evaluation
the picture worsens for the two grid-generalising champions: Gen 2 and
Gen 3 average 1.0163 and 1.0173 respectively (Table 4.2), and neither
finds a seed on which they beat `random` on this instance. The
`tightest_tw` baseline also loses here, and by a larger margin still
(mean 1.0455 across seeds — the largest baseline loss on any instance in
the grid). This is the only instance on which every non-`random`
configuration tested — one hand-designed rule and three LLM-evolved
candidates — produces a worse result than `random` in expectation. What
structural property of `lr102-10R` produces this pattern, and what it
implies for the reach of insertion-order-based heuristics on this
problem class, is discussed in Chapter 5.

## 4.6 Structural characteristics of the three champions

Gen 1's scoring function extracts seven features per pickup request —
earliest pickup time, pair slack (`l[d] − e[p]`), pickup-to-delivery
Euclidean distance, a cross-region flag, pickup demand, the pickup's region
coordinate, and the pickup's sweep angle around the instance centroid with
a randomly-sampled phase φ — min-max normalises them, and combines them
into a scalar score via a weighted linear sum with eight random weights
sampled uniformly per MSLP restart. The score contributions are signed:
earliest pickup, pair slack, sweep angle, and region-coordinate contribute
positively (later terms sort later); pickup-to-delivery distance, demand,
and cross-region flag contribute negatively. Pickups are then sorted
ascending by score to produce the returned permutation. The sweep-angle
component is the classical Gillett and Miller (1974) sweep heuristic,
originally developed for capacitated vehicle routing, adapted here to
PDPTW-SE by using the pickup centroid rather than a depot. Structurally,
Gen 1 is a **parallel weighted-sum scorer with per-restart weight
sampling**.

Gen 2 is structurally distinct from Gen 1 in every respect except the
signature. It extracts pickup and delivery coordinates, `ep`, and `ld` per
request; computes instance-level normalisation scales for distance and
time; samples four random weights (space, time, region, slack); selects a
starting pickup either as the earliest-`ep` request (with probability 0.3)
or uniformly at random; and then iteratively extends the ordering by
picking, at each step, the unvisited request that minimises a weighted
cost of distance from the current request's pickup or delivery to the next
pickup, a region-change penalty, a time-gap term, and a remaining-slack
term, with a small uniform jitter. Structurally, Gen 2 is a
**sequential, one-step-lookahead greedy chain constructor**.

Gen 3 is a **mixture of three construction strategies**, selected
uniformly by a random draw at every MSLP restart. With probability 0.50,
it applies a *cluster-then-lexicographic sort*: pickups are keyed by a
six-tuple whose leading components group by pickup region and prioritise
cross-region requests, tight pair slack, and early pickups. With
probability 0.25, it applies a *reverse-deadline lexicographic sort*: the
key inverts the sign of the latest-delivery time, then the latest-pickup
time, then the pair slack, ordering the tightest-deadline requests first.
With the remaining probability 0.25, it applies a *greedy spatio-temporal
nearest chain* whose structure closely mirrors Gen 2's chain
constructor but with a strict three-tuple lexicographic key (region
change, time gap, distance) for tie-breaking. The three strategies span
three distinct construction paradigms — cluster-then-sort, reverse
deadline, and greedy chain — and the LLM was invoked under the diversify
prompt (§3.6) that had explicitly asked for a structurally different
candidate rather than a refinement of the incumbent. The relationship
between the diversify prompt's family list (§3.6) and the three families
Gen 3 actually implements is discussed in Chapter 5.

## 4.7 Evolutionary plateau (generations 9–16)

*[Section to follow.]*