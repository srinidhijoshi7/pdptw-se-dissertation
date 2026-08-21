# Appendix E — Plateau Extension Full Log

This appendix reproduces the per-generation and per-candidate detail
of the second evolutionary session referenced in Section 4.7 and
Table 4.3. That session extended the search from the Gen 3 champion
`dacd3ec6f6c7` for a further eight generations under the identical
protocol (MODE = full, six-instance grid, seed 17, λ = 2,
`--mslpa = 10`), producing sixteen additional candidates none of which
matched or exceeded Gen 3's grid fitness of 0.9969. Table 4.3 in the
main body reports the per-generation best fitness across those eight
generations; this appendix supplies the underlying per-candidate hash,
per-candidate fitness, and per-generation prompt-kind and stagnation-
counter values that generated Table 4.3.

All values are drawn directly from the two archived JSONL logs:

- `src/python/llm_loop/logs/archive/generations_2026-08-11_gen9-16_extension.jsonl` — per-generation records (9 rows: seed row for gen 0 through gen 8)
- `src/python/llm_loop/logs/archive/candidates_2026-08-11_gen9-16_extension.jsonl` — per-candidate records (17 rows: seeded Gen 3 champion at gen 0 slot 0, plus 16 extension offspring at gen 1 slot 0 through gen 8 slot 1)

## E.1 Session provenance

- Session start (gen 0 seed): 2026-08-11T22:20:20 UTC
- Session end (gen 8): approximately 2026-08-11T22:59 UTC (based on gen 8 timestamps)
- Wall time: approximately 39 minutes for 16 candidate evaluations plus the seed replay
- Model: `gemini-3.6-flash` (SDK `google-genai==2.16.0`)
- Seed: 17
- Offspring per generation (λ): 2
- Stagnation threshold: 2 generations
- Evaluation grid: six instances as specified in Section 3.4
- Seed source: `champions/champion_seed.jl` set to Gen 3 (`dacd3ec6f6c7`), loaded directly at gen 0 as described in Section 3.5

## E.2 Per-generation record

Table E.1 reproduces the nine rows of the generations log, one per
generation from the seed row (gen 0, which replays the Gen 3 champion
for reference) through gen 8. `Prompt kind` is the prompt template
that fired in that generation (Section 3.6, Appendix B); `stagnation_gens`
is the stagnation counter value at the start of the generation, before
selection; `gen best hash` and `gen best fitness` are the content-hash
and fitness of the best of the λ = 2 offspring generated in that
generation.

**Table E.1.** Per-generation record of the extension session.

| Gen | Prompt kind | stagnation_gens | Gen best hash   | Gen best fitness | Δ vs Gen 3 (0.9969) |
|-----|-------------|-----------------|-----------------|------------------|---------------------|
| 0   | seed        | (n/a)           | `dacd3ec6f6c7`  | 0.9969           | 0.0000              |
| 1   | evolve      | 1               | `8614236645a6`  | 1.0150           | +0.0181             |
| 2   | evolve      | 2               | `c121cd2bbb02`  | 1.0190           | +0.0221             |
| 3   | diversify   | 3               | `9073550dc136`  | 1.0062           | +0.0093             |
| 4   | diversify   | 4               | `ae94ca2906b0`  | 1.0159           | +0.0190             |
| 5   | diversify   | 5               | `e54587a3b8fa`  | 1.0226           | +0.0257             |
| 6   | diversify   | 6               | `a026e86afd47`  | 1.0152           | +0.0183             |
| 7   | diversify   | 7               | `f0a749281654`  | 1.0069           | +0.0100             |
| 8   | diversify   | 8               | `7d58c56fc1da`  | 1.0086           | +0.0117             |

The eight extension generations reproduce Table 4.3 of the main body
exactly. Two structural facts about the run bear noting. First, the
stagnation counter increments monotonically from 1 (gen 1) to 8
(gen 8), consistent with the fact that no generation improves on the
Gen 3 champion. Second, the diversify prompt fires from gen 3 onward
— the first firing occurring at the stagnation threshold of 2 (Section 3.5)
— and continues to fire in every subsequent generation because
diversify itself never breaks the plateau, so the counter never
resets. Six diversify firings in total occur across the extension
session, and each produces a candidate with a distinct content hash
(rows 3 through 8 of Table E.1); no candidate is regenerated.

## E.3 Per-candidate record

Table E.2 reproduces the seventeen rows of the candidates log — the
seeded Gen 3 champion at gen 0 slot 0, plus the sixteen extension
offspring at gen 1 slot 0 through gen 8 slot 1. Slot 0 is the first
of the λ = 2 offspring generated in each generation; slot 1 is the
second. `Fitness` is the mean-of-ratios grid fitness (Section 3.4);
values below 0.9969 would beat the incumbent Gen 3 champion, and
values above 0.9969 do not. `Winner` indicates the slot that produced
the best fitness in each generation.

**Table E.2.** Per-candidate record of the extension session
(17 rows: 1 seed + 16 offspring).

| Gen | Slot | Code hash       | Fitness | Δ vs Gen 3 (0.9969) | Winner |
|-----|------|-----------------|---------|---------------------|--------|
| 0   | 0    | `dacd3ec6f6c7`  | 0.9969  | 0.0000              | (seed) |
| 1   | 0    | `8614236645a6`  | 1.0150  | +0.0181             | ✓      |
| 1   | 1    | `52a1b648af2e`  | 1.0166  | +0.0197             |        |
| 2   | 0    | `c121cd2bbb02`  | 1.0190  | +0.0221             | ✓      |
| 2   | 1    | `4e788c2cbf8b`  | 1.0303  | +0.0334             |        |
| 3   | 0    | `2d39a3fc6f60`  | 1.0338  | +0.0369             |        |
| 3   | 1    | `9073550dc136`  | 1.0062  | +0.0093             | ✓      |
| 4   | 0    | `ae94ca2906b0`  | 1.0159  | +0.0190             | ✓      |
| 4   | 1    | `f4ee3d1c23e6`  | 1.0186  | +0.0217             |        |
| 5   | 0    | `e54587a3b8fa`  | 1.0226  | +0.0257             | ✓      |
| 5   | 1    | `cf67c3709395`  | 1.0309  | +0.0340             |        |
| 6   | 0    | `b649fa33c797`  | 1.0273  | +0.0304             |        |
| 6   | 1    | `a026e86afd47`  | 1.0152  | +0.0183             | ✓      |
| 7   | 0    | `46dd526de1e2`  | 1.0250  | +0.0281             |        |
| 7   | 1    | `f0a749281654`  | 1.0069  | +0.0100             | ✓      |
| 8   | 0    | `7d58c56fc1da`  | 1.0086  | +0.0117             | ✓      |
| 8   | 1    | `0c62463937e8`  | 1.0242  | +0.0273             |        |

Sixteen offspring, sixteen distinct content hashes — no candidate is
regenerated from the LLM at any point in the session, and none
matches the Gen 3 seed's grid fitness of 0.9969. The best-of-run
offspring is `9073550dc136` at gen 3 slot 1 (fitness 1.0062, 0.93%
above Gen 3), produced by the first firing of the diversify prompt.
The worst-of-run offspring is `2d39a3fc6f60` at gen 3 slot 0
(fitness 1.0338, 3.69% above Gen 3), produced in the same generation
as the best-of-run — evidence of the wide per-generation fitness
spread the (1+λ = 2) strategy tolerates.

## E.4 Aggregate across sessions

Combining the eight generations of the extension session reported here
with the eight generations of the original session that produced Gen 3
(Section 4.2 and Section 4.7), the full-grid trajectory spans sixteen
generations and thirty-two candidate evaluations. Across those
thirty-two candidates, three winners emerge (Gen 1 `d1791ed1796e`,
Gen 2 `cbbe47d2468c`, Gen 3 `dacd3ec6f6c7`, all from the original
session), and no candidate in the extension session matches or
exceeds Gen 3's seed-17 grid fitness of 0.9969. The empirical case
for treating Gen 3 as the terminal champion of the full-grid trajectory
at this specific fixed evaluation configuration
({seed 17, `--mslpa = 10`, `gemini-3.6-flash`, λ = 2}) rests on this
thirty-two-candidate evidence base.

Section 5.4 develops the interpretation of this plateau in terms of
four candidate explanations — search-budget insufficiency,
model-capability ceiling, evaluation-harness signal saturation, and
grid diversity insufficient to reward further exploration — and
refuses to pick among them without further experimental evidence.
The distinguishing experiments that would identify which of the four
mechanisms dominates are the subject of Chapter 6's future-work
section.