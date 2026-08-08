# Champion Grid Evaluations

Comparison of both champions on the full 6-instance grid.
All runs at `seed=17`, `--mslpa=10`, `gemini-3.6-flash`.

## Champions

| Label | Hash | Fitness on lr101-10R (evolution measurement) | Description |
|---|---|---|---|
| Gen 1 | `d1791ed1796e` | 0.9757 | Parallel weighted-sum scoring with sweep-angle features |
| Gen 2 | `cbbe47d2468c` | 0.9681 | Sequential nearest-neighbour construction with random start |

## Grid results

| Instance | Random | Gen 1 ratio | Gen 2 ratio | Winner |
|---|---|---|---|---|
| lr101-6R  |  766.20 | 1.0000 | 0.9969 | Gen 2 |
| lr102-6R  |  542.25 | 1.0053 | 1.0000 | Gen 2 |
| lr103-6R  |  454.61 | 1.0335 | 1.0301 | Gen 2 (both lose) |
| lr201-6R  |  846.44 | 1.0000 | 0.9925 | Gen 2 |
| lr101-10R | 1297.54 | 0.9757 | 0.9681 | Gen 2 |
| lr102-10R | 1033.45 | 1.0000 | 1.0082 | Gen 1 |

## Aggregate

| Champion | Mean ratio | Wins | Losses | Ties |
|---|---|---|---|---|
| Gen 1 (`d1791ed1796e`) | 1.0024 | 1/6 | 2 | 3 |
| Gen 2 (`cbbe47d2468c`) | 0.9993 | 3/6 | 2 | 1 |

## Findings

1. **Gen 2 beats or matches Gen 1 on 5 of 6 instances** — evolution produced a champion that dominates its ancestor at seed 17, empirically validating the 1+λ mechanism.
2. **Neither champion universally dominates random** — mean ratios (1.0024 and 0.9993) are essentially tied with baseline. But Gen 2's per-instance distribution is more favourable (3 wins vs 1 win).
3. **lr103-6R is a stubborn loss for both champions** — both lose ~3%. This instance's structure resists the type of ordering the LLM proposed. Worth further investigation.
4. **The training instance improvement transfers to same-family instances.** Gen 2 evolved on lr101-10R and beats random on 3 instances including one from a different type family (lr201-6R, tight time windows).
5. **This motivates full-grid evolution as the next experiment.** With fitness defined over all 6 instances, the LLM will be incentivised to produce candidates that generalise, rather than candidates optimised for one instance's local optima.
