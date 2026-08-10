# Champion Grid Evaluations

Comparison of all champions on the full 6-instance grid.
All runs at `seed=17`, `--mslpa=10`, `gemini-3.6-flash`.

## Champions

| Label | Hash | Evolution mode | Description |
|---|---|---|---|
| Gen 1 | `d1791ed1796e` | dev (lr101-10R) | Parallel weighted-sum scoring with sweep-angle features |
| Gen 2 | `cbbe47d2468c` | dev (lr101-10R) | Sequential nearest-neighbour construction with random start |
| Gen 3 | `dacd3ec6f6c7` | full (6-instance grid) | Emerged from diversify prompt after 2-gen stagnation |

## Grid results

| Instance | Random | Gen 1 | Gen 2 | Gen 3 | Best |
|---|---|---|---|---|---|
| lr101-6R  |  766.20 | 1.0000 | 0.9969 | 1.0000 | Gen 2 |
| lr102-6R  |  542.25 | 1.0053 | 1.0000 | 1.0000 | Gen 2 |
| lr103-6R  |  454.61 | 1.0335 | 1.0301 | **0.9989** | Gen 3 |
| lr201-6R  |  846.44 | 1.0000 | 0.9925 | 1.0000 | Gen 2 |
| lr101-10R | 1297.54 | 0.9757 | 0.9681 | 0.9744 | Gen 2 |
| lr102-10R | 1033.45 | 1.0000 | 1.0082 | 1.0082 | Gen 1 |

## Aggregate

| Champion | Mean ratio | Wins | Losses | Ties |
|---|---|---|---|---|
| Gen 1 (`d1791ed1796e`) | 1.0024 | 1/6 | 2 | 3 |
| Gen 2 (`cbbe47d2468c`) | 0.9993 | 3/6 | 2 | 1 |
| **Gen 3 (`dacd3ec6f6c7`)** | **0.9969** | 2/6 | 1 | 3 |

## Findings

1. **Mean grid fitness monotonically improved across the three champions** (1.0024 → 0.9993 → 0.9969). Each is strictly the best on the metric it was optimised for.

2. **Gen 2 has more per-instance wins than Gen 3.** This is not a contradiction — Gen 2 was evolved on a single instance and found deeper specialised optima there. Gen 3 was evolved on the whole grid and traded some specialisation for generalisation.

3. **Gen 3 is the first champion to beat random on lr103-6R.** All previous champions lost ~3% on this instance. Full-mode fitness pressure discovered an ordering that fixes it.

4. **lr102-10R is a persistent negative result.** No champion beats random on this instance; Gen 2 and Gen 3 both lose ~0.82%. This suggests a structural feature of lr102-10R that resists the ordering paradigms Gemini produced. Worth investigating as future work.

5. **The diversify prompt was decisive in Gen 3's discovery.** After two stagnant generations under the evolve prompt in the full-mode run, the diversify prompt fired at generation 3 and its first slot produced the new champion. First empirical evidence of the diversify mechanism directly contributing a winning candidate.

6. **Full-mode gains are smaller in absolute magnitude than dev-mode gains** (0.31% below random on grid vs 3.19% below random on lr101-10R). This is expected: single-instance fitness allows sharper specialisation, but grid fitness measures what actually generalises.
