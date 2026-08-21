# Appendix D — Multi-Seed Evaluation Full Detail

This appendix reproduces the full per-seed, per-instance ratio detail
underlying the multi-seed variance analysis reported in Table 4.2 and
Figure 4.1. The main-body table gives aggregate mean and standard
deviation across the five evaluation seeds; this appendix supplies the
raw per-seed ratios that generated those aggregates, together with the
random-baseline variance across seeds, the wins–losses–ties tally that
motivates the interpretive framing in Section 5.2, and the run
provenance metadata. All values are drawn directly from
`src/python/llm_loop/results/champions_multi_seed_summary.md` and the
underlying `multi_seed_evaluation.json`, both of which are archived
in the project repository.

## D.1 Run provenance

The multi-seed evaluation was executed as a single continuous run
against the six-instance grid, comprising 150 MSLP invocations in
total: 30 baseline evaluations (two baseline rules × five seeds ×
six instances, with `random` and `tightest_tw` each evaluated once
per (seed, instance) pair) and 90 champion evaluations (three
champions × five seeds × six instances). All 150 runs completed
without failure.

**Configuration:**

- Seeds: {17, 42, 100, 200, 500}
- Instances: `06R_06V_02I_04M/t1/{lr101, lr102, lr103}`,
  `06R_06V_02I_04M/t2/lr201`,
  `10R_10V_02I_04M/t1/{lr101, lr102}`
- Champions evaluated: `Gen1_d1791ed1796e`, `Gen2_cbbe47d2468c`,
  `Gen3_dacd3ec6f6c7`
- Baseline rules evaluated: `random`, `tightest_tw`
- `--mslpa`: 10, `--alpha`: 0.05, `--max_time`: 60 s, `--threads`: 1
- Started: 2026-08-11T17:48:40 UTC
- Finished: 2026-08-11T18:10:35 UTC
- Wall time: approximately 22 minutes for 150 runs

**Data files (repository paths):**

- `src/python/llm_loop/results/multi_seed_evaluation.json` — raw per-run cost, elapsed time, and exit code
- `src/python/llm_loop/results/multi_seed_runs.jsonl` — line-per-run log of the same
- `src/python/llm_loop/results/champions_multi_seed_summary.md` — aggregated summary tables (subset reproduced below)

## D.2 Random baseline variance across seeds

Because ratios in the aggregate table (Table 4.2) are computed against
the same-seed `random` baseline, understanding how much the baseline
itself varies across seeds is prerequisite to interpreting the ratio
variances. Table D.1 reports the mean, standard deviation, and sample
size for the `random` baseline cost on each instance across the five
seeds.

**Table D.1.** Random baseline cost by instance across seeds
{17, 42, 100, 200, 500}, `--mslpa = 10`.

| Instance                     | Mean cost | Std   | n |
|------------------------------|-----------|-------|---|
| `06R_06V_02I_04M/t1/lr101`   | 764.36    | 1.05  | 5 |
| `06R_06V_02I_04M/t1/lr102`   | 542.25    | 0.00  | 5 |
| `06R_06V_02I_04M/t1/lr103`   | 455.27    | 5.52  | 5 |
| `06R_06V_02I_04M/t2/lr201`   | 849.89    | 7.71  | 5 |
| `10R_10V_02I_04M/t1/lr101`   | 1326.05   | 66.69 | 5 |
| `10R_10V_02I_04M/t1/lr102`   | 1026.24   | 10.86 | 5 |

Three observations follow from Table D.1. First, `lr102-6R` shows zero
variance across seeds — `random` returns cost 542.25 at every seed —
which explains why every non-`random` configuration on that instance
shows a per-seed ratio that is either exactly 1.0000 or a fixed
constant, with no seed-to-seed variability in the ratio itself.
Second, `lr101-10R` shows a standard deviation of 66.69 on a mean of
1326.05 — a coefficient of variation of approximately 5% —
substantially larger than any other instance and consistent with the
large per-seed ratio variance every candidate exhibits on this
instance (Section 4.4, Figure 4.1). Third, the 6-request instances
generally show smaller absolute variance than the 10-request
instances, consistent with the intuition that MSLP at `--mslpa = 10`
saturates more readily on smaller problems.

## D.3 Aggregate ratios reproduced

Table D.2 reproduces Table 4.2 from the main body verbatim, for
convenience of reference within this appendix. Values are mean and
standard deviation of the per-seed ratio to the same-seed `random`
baseline (n = 5 in each cell); lower is better; bolded values are the
best (lowest) mean in each row. The header row uses the champion
content-hash tags used throughout the repository.

**Table D.2.** Champion ratios to same-seed random baseline across
seeds {17, 42, 100, 200, 500}.

| Instance                     | `tightest_tw`         | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`)   |
|------------------------------|-----------------------|------------------------|------------------------|--------------------------|
| `06R_06V_02I_04M/t1/lr101`   | 1.0024 ± 0.0014       | 1.0011 ± 0.0019        | **0.9994 ± 0.0014**    | 1.0024 ± 0.0014          |
| `06R_06V_02I_04M/t1/lr102`   | 1.0053 ± 0.0000       | 1.0011 ± 0.0024        | **1.0000 ± 0.0000**    | 1.0021 ± 0.0029          |
| `06R_06V_02I_04M/t1/lr103`   | 1.0163 ± 0.0122       | 1.0287 ± 0.0375        | 1.0198 ± 0.0145        | **0.9943 ± 0.0121**      |
| `06R_06V_02I_04M/t2/lr201`   | 0.9960 ± 0.0089       | 1.0200 ± 0.0201        | **0.9930 ± 0.0082**    | 0.9960 ± 0.0089          |
| `10R_10V_02I_04M/t1/lr101`   | 1.0123 ± 0.0714       | **0.9814 ± 0.0831**    | 1.0065 ± 0.0496        | 1.0025 ± 0.0993          |
| `10R_10V_02I_04M/t1/lr102`   | 1.0455 ± 0.0110       | **1.0068 ± 0.0143**    | 1.0163 ± 0.0117        | 1.0173 ± 0.0126          |
| **Mean across instances**    | 1.0130 ± 0.0175       | 1.0065 ± 0.0265        | 1.0058 ± 0.0142        | **1.0024 ± 0.0229**      |

## D.4 Per-seed ratios by instance

Tables D.3 through D.8 supply the 30 per-seed ratios that were
aggregated into each row of Table D.2. The rows of each sub-table are
the five evaluation seeds; the columns are the random baseline cost at
that seed followed by the per-candidate ratio to that baseline.
Ratios below 1.000 mean the candidate beat `random` on that
(seed, instance) pair; ratios above 1.000 mean it lost; 1.0000
denotes exact parity.

**Table D.3.** Per-seed ratios on `06R_06V_02I_04M/t1/lr101`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 766.20        | 1.0000        | 1.0000                 | 0.9969                 | 1.0000                 |
| 42   | 763.79        | 1.0032        | 1.0032                 | 1.0000                 | 1.0032                 |
| 100  | 763.79        | 1.0032        | 1.0032                 | 1.0000                 | 1.0032                 |
| 200  | 764.25        | 1.0026        | 0.9994                 | 1.0000                 | 1.0026                 |
| 500  | 763.79        | 1.0032        | 1.0000                 | 1.0000                 | 1.0032                 |

**Table D.4.** Per-seed ratios on `06R_06V_02I_04M/t1/lr102`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 542.25        | 1.0053        | 1.0053                 | 1.0000                 | 1.0000                 |
| 42   | 542.25        | 1.0053        | 1.0000                 | 1.0000                 | 1.0000                 |
| 100  | 542.25        | 1.0053        | 1.0000                 | 1.0000                 | 1.0053                 |
| 200  | 542.25        | 1.0053        | 1.0000                 | 1.0000                 | 1.0053                 |
| 500  | 542.25        | 1.0053        | 1.0000                 | 1.0000                 | 1.0000                 |

**Table D.5.** Per-seed ratios on `06R_06V_02I_04M/t1/lr103`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 454.61        | 1.0176        | 1.0335                 | 1.0301                 | 0.9989                 |
| 42   | 452.25        | 1.0229        | 1.0052                 | 1.0355                 | 1.0000                 |
| 100  | 464.98        | 0.9949        | 1.0071                 | 1.0104                 | 0.9726                 |
| 200  | 452.25        | 1.0229        | 1.0052                 | 1.0000                 | 1.0000                 |
| 500  | 452.25        | 1.0229        | 1.0922                 | 1.0229                 | 1.0000                 |

**Table D.6.** Per-seed ratios on `06R_06V_02I_04M/t2/lr201`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 846.44        | 1.0000        | 1.0000                 | 0.9925                 | 1.0000                 |
| 42   | 846.44        | 1.0000        | 1.0000                 | 1.0000                 | 1.0000                 |
| 100  | 846.44        | 1.0000        | 1.0204                 | 1.0000                 | 1.0000                 |
| 200  | 846.44        | 1.0000        | 1.0370                 | 0.9925                 | 1.0000                 |
| 500  | 863.69        | 0.9800        | 1.0428                 | 0.9800                 | 0.9800                 |

**Table D.7.** Per-seed ratios on `10R_10V_02I_04M/t1/lr101`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 1297.54       | 0.9908        | 0.9757                 | 0.9681                 | 0.9744                 |
| 42   | 1398.44       | 1.0167        | 0.9005                 | 0.9880                 | 0.9111                 |
| 100  | 1266.30       | 1.0152        | 1.0891                 | 1.0934                 | 1.1095                 |
| 200  | 1270.58       | 1.1190        | 1.0388                 | 0.9887                 | 1.1057                 |
| 500  | 1397.38       | 0.9200        | 0.9031                 | 0.9944                 | 0.9118                 |

**Table D.8.** Per-seed ratios on `10R_10V_02I_04M/t1/lr102`.

| Seed | random (cost) | `tightest_tw` | Gen 1 (`d1791ed1796e`) | Gen 2 (`cbbe47d2468c`) | Gen 3 (`dacd3ec6f6c7`) |
|------|---------------|---------------|------------------------|------------------------|------------------------|
| 17   | 1033.45       | 1.0382        | 1.0000                 | 1.0082                 | 1.0082                 |
| 42   | 1018.62       | 1.0533        | 1.0278                 | 1.0278                 | 1.0278                 |
| 100  | 1018.62       | 1.0533        | 1.0146                 | 1.0229                 | 1.0229                 |
| 200  | 1041.90       | 1.0297        | 0.9919                 | 1.0000                 | 1.0000                 |
| 500  | 1018.62       | 1.0533        | 1.0000                 | 1.0229                 | 1.0278                 |

## D.5 Wins–losses–ties by candidate

For each candidate, Table D.9 counts the number of instances on which
the candidate's mean ratio across the five seeds beats `random`
(mean ratio < 0.999), loses to `random` (mean ratio > 1.001), or ties
(mean ratio within ±0.001 of 1.000). This aggregation gives the
picture the mean-of-means alone obscures: whether a candidate's
overall mean is close to parity because it beats `random` on some
instances and loses on others, or because it ties everywhere.

**Table D.9.** Instance-level wins, losses, and ties per candidate
(mean ratio across five seeds vs 1.000).

| Candidate                | Wins | Losses | Ties |
|--------------------------|------|--------|------|
| `tightest_tw`            | 1    | 5      | 0    |
| Gen 1 (`d1791ed1796e`)   | 1    | 5      | 0    |
| Gen 2 (`cbbe47d2468c`)   | 1    | 3      | 2    |
| Gen 3 (`dacd3ec6f6c7`)   | 2    | 4      | 0    |

Reading Table D.9 alongside Table D.2 recovers the per-instance
picture that motivates the honest interpretive framing of Section 5.2.
`tightest_tw` wins only on `lr201-6R` (mean 0.9960) and loses on the
other five instances. Gen 1 wins only on `lr101-10R` (mean 0.9814) —
the instance it was originally evolved on — and loses on the other
five. Gen 2 wins on `lr101-6R` (mean 0.9994), ties on `lr102-6R` (mean
1.0000) and `lr201-6R` is a further win in mean (0.9930), while losing
on the three remaining. Gen 3 wins on `lr103-6R` (mean 0.9943, and
consistently across all five seeds) and `lr201-6R` (mean 0.9960), and
loses on the other four.

The pattern that emerges is that no candidate universally beats
`random` in mean across the grid: each candidate wins on the
subset of instances where its structural bias aligns with the
instance's structure, and loses on the rest. Section 5.2 develops this
into the answer to RQ2 — that improvements are real but
instance-specific rather than uniform — and Section 5.5 develops the
`lr102-10R` losses across all four non-`random` configurations into
the argument that the persistent negative reflects a limitation of
insertion-order-based heuristics as a class.