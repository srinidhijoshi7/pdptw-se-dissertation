# Gen 9–16 Evolution Extension: Plateau Confirmed

Extended the evolutionary search from Gen 3 champion `dacd3ec6f6c7`
(grid fitness 0.9969 at seed 17) for a further 8 generations, λ=2,
under the same full-grid fitness signal used originally.

## Result

All 16 candidates worse than Gen 3. Best of run: 1.0062 (Gen 3 slot 1
of the extension, diversify prompt). Champion unchanged for all 8
extension generations.

## Per-generation best fitness (extension)

| Gen | Prompt | Best candidate fitness | Delta vs champion (0.9969) |
|---|---|---|---|
| 1 | evolve    | 1.0150 | +0.0181 |
| 2 | evolve    | 1.0190 | +0.0221 |
| 3 | diversify | 1.0062 | +0.0093 |
| 4 | diversify | 1.0159 | +0.0190 |
| 5 | diversify | 1.0226 | +0.0257 |
| 6 | diversify | 1.0152 | +0.0183 |
| 7 | diversify | 1.0069 | +0.0100 |
| 8 | diversify | 1.0086 | +0.0117 |

## Interpretation

Sixteen total generations (Chat 06 gens 1–8 + this extension gens 9–16)
produced 32 candidates. None matched or exceeded Gen 3's grid fitness
of 0.9969. The diversify prompt fired 6 times in this extension and
generated candidates with distinct code hashes each time (no
regeneration of prior candidates), but no candidate broke the plateau.

No candidate matched Gen 3's seed-17 grid fitness of 0.9969 across 16 additional generations, providing empirical evidence of a plateau at this specific fitness configuration (seed 17, --mslpa=10, gemini-3.6-flash, λ=2). This is a plateau in the evolutionary search under a fixed evaluation configuration — not a claim about generalisation across seeds, which is characterised separately in the multi-seed evaluation.

Gen 3 `dacd3ec6f6c7` is therefore the terminal champion of the
evolutionary search reported in the dissertation.

## Log files

- `logs/gen9_to_16_run.log`: full tee'd terminal output
- `logs/archive/candidates_2026-08-11_gen9-16_extension.jsonl`
- `logs/archive/generations_2026-08-11_gen9-16_extension.jsonl`
