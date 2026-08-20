# Abstract

This dissertation tests whether the paradigm of large-language-model-driven
evolutionary program search, established by FunSearch (Romera-Paredes et al.,
2024), extends to the Pickup and Delivery Problem with Time Windows and
Scheduling on the Edges, introduced by Barbosa, Tiwari and Melo (2026). A
pipeline was built targeting the `get_service_order` dispatcher inside their
Multi-Start LP-Improvement heuristic: a Python driver embeds `gemini-3.6-flash`
in a (1+λ = 2) evolutionary loop; a three-prompt cascade of seed, evolve, and
diversify prompts adapts the language model's role to the loop's state; each
candidate Julia function is injected into MSLP at runtime and scored by mean
ratio of solution cost to a same-seed random baseline across six multi-island
Type 1 benchmark instances. Three successive champions emerged across sixteen
generations of full-grid evolution, exhibiting monotonically improving mean
grid fitness. Multi-seed re-evaluation across five random seeds established
that all three champions decisively outperform the paper's tightest-time-window
baseline, and that the strongest — a probabilistic mixture of three
structurally distinct strategies produced by the diversify prompt after two
consecutive stagnation generations — partially outperforms the random baseline,
beating it consistently on one instance and in mean on another. No candidate
across a subsequent eight-generation session improved on this champion,
confirming a plateau at this specific evaluation configuration. The findings
confirm the FunSearch paradigm on a richer combinatorial setting than
previously tested, identify a compositional prompt-following behaviour in
which the language model treated the diversify prompt's family menu as
palette rather than selection list, and locate the persistent negative on
one benchmark instance as a limitation of insertion-order-based heuristics
as a class rather than of the specific pipeline.
