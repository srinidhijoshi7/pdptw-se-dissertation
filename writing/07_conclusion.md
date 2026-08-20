# Chapter 6 — Conclusion

*[Target: ~1000 words.]*

## 6.1 Summary of contributions

This dissertation set out to test whether large language models,
embedded in an evolutionary loop, could discover insertion-scoring
functions that improve on hand-designed baselines within the
Multi-Start LP-Improvement heuristic for the Pickup and Delivery
Problem with Time Windows and Scheduling on the Edges (Barbosa,
Tiwari and Melo, 2026). Three contributions delivered on that test.

The first contribution is a working end-to-end pipeline targeting the
`get_service_order` dispatcher inside MSLP. This includes the technical
mechanism that enables runtime code loading of LLM-generated Julia
functions into the compiled heuristic (Section 3.3), the (1+λ)
evolutionary loop with elitist selection and stagnation-triggered
diversification (Section 3.5), the three-prompt cascade of seed, evolve
and diversify prompts (Section 3.6), and the fitness harness with
same-seed baseline discipline (Section 3.4). The pipeline is committed
to a private Git repository alongside every candidate, generation log,
and result artefact used in this dissertation; the central Chapter 4
reproduction can be regenerated on a fresh machine in approximately
twenty minutes with only Julia and Gurobi installed.

The second contribution is an empirical characterisation of the
pipeline's behaviour on the multi-island (Type 1) benchmark family.
Three successive champions were produced across sixteen generations
of full-grid evolution, exhibiting monotonically improving mean grid
fitness. Multi-seed re-evaluation across five random seeds established
that all three champions decisively outperform the paper's
`tightest_tw` baseline; that the third champion partially outperforms
the `random` baseline, beating it consistently on the `lr103-6R`
instance and in mean on `lr201-6R`; and that no further improvement
was found across a second eight-generation session, confirming the
third champion as a terminal plateau of this configuration.

The third contribution is an interpretive account of what the pipeline
produced. The Gen 3 champion emerged from the diversify prompt at
exactly the anticipated stagnation point and composed three of the
five prompted strategy families into a probabilistic mixture — a
compositional behaviour the prompt did not instruct and that the
evolve-driven predecessors did not exhibit. The plateau at Gen 3 is
best treated as an interaction of four candidate mechanisms (Section
5.4) rather than a single cause, and the persistent negative result
on `lr102-10R` reflects a limitation of insertion-order-based
heuristics as a class rather than of this specific pipeline. Positioned
against FunSearch (Romera-Paredes et al., 2024), Evolution of Heuristics
(Liu et al., 2024), and ReEvo (Ye et al., 2024), the results confirm
the core paradigm on a richer combinatorial setting than previously
tested, complicate the implicit population-size claim of prior work,
and identify reflection-style mechanisms as the natural next
architectural extension.

## 6.2 Answers to the research questions



## 6.3 Future work
