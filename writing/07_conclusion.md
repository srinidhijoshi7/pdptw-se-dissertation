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

The dissertation's three sub-questions admit the following compact
answers, developed in full in Section 5.2.

**RQ1 (baseline comparison).** LLM-evolved candidates decisively
outperform the `tightest_tw` baseline; they partially outperform the
`random` baseline. All three champions produce a lower multi-seed mean
grid ratio than `tightest_tw` (1.0130), with the third champion at
1.0024. No champion produces a mean ratio strictly below 1.000 across
the five-seed evaluation, so none beats `random` on average across the
grid; the seed-17 result reported in Section 4.3 is a favourable slice
rather than the seed-averaged verdict.

**RQ2 (seed generalisation).** Improvements are real but
instance-specific rather than uniform. The third champion beats
`random` on `lr103-6R` across all five evaluation seeds and on
`lr201-6R` in mean, while `lr101-10R` exhibits large per-seed variance
irrespective of the candidate used, and `lr102-10R` remains a
negative case for every non-`random` configuration tested.

**RQ3 (structural characteristics).** The three champions exhibit
three qualitatively different construction paradigms — parallel
weighted-sum scoring, sequential greedy chain construction, and a
uniformly-selected mixture of three strategies. The strongest of the
three is the one that abandoned single-strategy commitment for a
probabilistic mixture, produced by the diversify prompt after two
consecutive stagnation generations. The mixture-of-strategies
architecture was the LLM's own initiative rather than the prompt's
instruction.

## 6.3 Future work

Four extensions to this work are worth naming concretely. Each
targets a specific limitation identified in Section 5.4 or Section
5.5, and each requires resources beyond those available to this
dissertation.

The first extension is a scaling of the evolutionary budget. The
(1+λ = 2) strategy used here is a quota-driven compression of the
larger populations used by FunSearch and by the Evolution of
Heuristics framework. A comparable pipeline run at (1+λ = 5) or
(µ + λ) with populations of ten or more, across enough generations
to test whether the Gen 3 plateau reflects search-budget
insufficiency rather than mechanism failure, would require an API
subscription and roughly a week of wall-time.

The second extension is a multi-model comparison. This dissertation
evaluates only `gemini-3.6-flash`, one model in one capability tier.
Running the same pipeline with a higher-capability model (a larger
Gemini variant, or a comparable model from another vendor) on the
same benchmark and prompt cascade would distinguish the
model-capability ceiling hypothesis (Section 5.4, Explanation 2) from
the other candidate explanations. Roughly a day of setup and half a
day of runtime per model.

The third extension is a broadening of the evaluation grid.
Multi-floor (Type 2) benchmark instances and larger request counts
were deferred as stretch scope; expanding the grid to include them
would test whether the plateau at Gen 3 reflects an implicit
effective sample size of two (Section 5.4, Explanation 4) or a more
fundamental limit. Rebuilding baselines at the expanded grid across
five seeds requires roughly two days of Julia runtime.

The fourth and most substantive extension addresses the persistent
negative on `lr102-10R`. The failure of every insertion-order-based
configuration on that instance suggests that the natural next
architectural move is a change of injection point: evolving a
ruin-and-recreate operator inside a large-neighbourhood-search
wrapper (Ropke and Pisinger, 2006), where the LLM's contribution
determines which requests to remove and reinsert rather than in what
order to construct. This would also open a natural path to
incorporating a reflection layer between generations (Ye et al.,
2024) as the mechanism for accumulating design hints across the
larger search space that ruin-and-recreate opens up. This extension
is a research programme, not a follow-up experiment, and would
sit as a natural PhD topic.