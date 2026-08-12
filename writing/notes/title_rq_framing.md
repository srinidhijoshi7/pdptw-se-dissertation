# Title, Research Question, Abstract Seed

*Working anchor document. Everything in the dissertation must be consistent with this. If title, RQ, or abstract changes, update all three here first.*

## Working title

Evolving Insertion Heuristics with Large Language Models: A Case Study on the Pickup and Delivery Problem with Time Windows and Scheduling on the Edges

## Primary research question

Can large language models, embedded in a FunSearch-style evolutionary loop, discover insertion-scoring functions that improve on hand-designed baselines within Barbosa, Tiwari and Melo's (2026) Multi-Start LP-Improvement heuristic for the PDPTW-SE?

## Sub-questions

- **RQ1.** How do LLM-evolved candidates compare against the two hand-designed baselines (`random`, `tightest_tw`) across the multi-island (Type 1) benchmark?
- **RQ2.** Do improvements observed at a fixed evaluation seed generalise across seed variation, or are they seed-specific artefacts of a stochastic evaluator?
- **RQ3.** What structural characteristics emerge in successful candidates, and what do the successes and failures reveal about the mechanism and limits of LLM-driven heuristic evolution in constrained combinatorial optimisation?

## Abstract seed (~120 words, will expand to ~250 in final)

This dissertation applies the FunSearch (Romera-Paredes et al., 2024) and Evolution of Heuristics (Liu et al., 2024) paradigm of language-model-driven algorithm discovery to the Pickup and Delivery Problem with Time Windows and Scheduling on the Edges (PDPTW-SE), introduced by Barbosa, Tiwari and Melo (2026). Gemini is embedded in a 1+λ evolutionary loop that proposes candidate insertion-scoring functions in Julia, each evaluated by running the Multi-Start LP-Improvement heuristic on a six-instance multi-island benchmark. Three champions emerged across sixteen generations. Multi-seed evaluation reveals monotonic mean-ratio improvement across generations and consistent gains over the hand-designed `tightest_tw` baseline, with per-instance wins that vary in structurally interpretable ways.

## Mapping of sub-RQs to chapter sections

- RQ1 → Chapter 4 §4.2 (three-champion progression) and §4.4 (per-instance analysis)
- RQ2 → Chapter 4 §4.3 (multi-seed variance evaluation)
- RQ3 → Chapter 5 §5.1–5.5 (structural interpretation, plateau, lr102-10R)

## Notes for later revision

- Title may shorten if word count is tight — fallback: "LLM-Driven Heuristic Evolution for the PDPTW-SE"
- Abstract expands to ~250 words after final results table exists; add quantitative headline in the expanded version