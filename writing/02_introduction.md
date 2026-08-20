# Chapter 1 — Introduction

*[Target: ~1500 words. Write last-but-one, after Chapters 2–5 exist.]*

## 1.1 Motivation

Real-world logistics settings routinely involve pickup and delivery
requests distributed across regions connected by scheduled
infrastructure — inter-island ferries whose sailings depend on tidal
windows, elevators in multi-storey hospitals whose availability shifts
with staffing, aircraft moving cargo between airports on published
timetables. Solving such a problem requires deciding, jointly, which
vehicles serve which requests, in what order, and how the shared
infrastructure that links regions is scheduled to carry the vehicles
across. The Pickup and Delivery Problem with Time Windows and
Scheduling on the Edges — introduced by Barbosa, Tiwari and Melo (2026)
as a formalisation of this class of problem — combines routing under
time-window feasibility with the scheduling of the machines that link
regions into a single integrated optimisation. It is a very recent
addition to the pickup-and-delivery family, published in January 2026,
and solving it exactly is intractable at the instance sizes real
deployments require. The state of the art on realistic instances is a
Multi-Start LP-Improvement heuristic, MSLP, proposed in the same paper.

Heuristics of this kind depend on a small number of hand-designed
components: the order in which requests are considered for insertion,
the tie-breaking rules used to resolve near-equivalent choices, the
restart strategies that govern the multi-start loop. These components
are typically the product of researcher intuition supplemented by
empirical tuning, and they represent a real bottleneck on heuristic
performance: only what a researcher happens to conceive of gets tested,
and the space of plausible alternatives remains largely unexplored. The
recent emergence of LLM-driven algorithm discovery, initiated by
FunSearch (Romera-Paredes et al., 2024) and extended by subsequent
work, opens a different route. A code-generating language model,
coupled with a systematic evaluator that filters proposals by measured
performance, can propose and refine heuristic components with a
throughput and structural diversity that hand design cannot match.

Whether this paradigm extends to a research-grade heuristic for the
PDPTW-SE — specifically, whether an LLM embedded in an evolutionary
loop can discover useful insertion-scoring functions inside MSLP — is
the question this dissertation asks. The problem's novelty is a
feature rather than an obstacle: the paradigm has not previously been
tested on a routing problem with the PDPTW-SE's combination of
integer scheduling constraints and inter-region synchronisation, and
the results reported in this dissertation are the first empirical
evidence of what LLM-driven heuristic evolution can and cannot do in
this specific setting.

## 1.2 Research question and sub-questions

The primary research question this dissertation addresses is: **can large
language models, embedded in a FunSearch-style evolutionary loop, discover
insertion-scoring functions that improve on hand-designed baselines within
Barbosa, Tiwari and Melo's (2026) Multi-Start LP-Improvement heuristic for
the PDPTW-SE?** Three sub-questions refine this primary question into
testable form. **RQ1** asks how LLM-evolved candidates compare against
the two hand-designed baselines — a uniform random shuffle and a
tightest-time-window sort — across the multi-island (Type 1) benchmark.
**RQ2** asks whether improvements observed at a fixed evaluation seed
generalise across seed variation, or whether they are seed-specific
artefacts of a stochastic evaluator. **RQ3** asks what structural
characteristics emerge in the candidates the loop produces, and what the
successes and failures reveal about the mechanism and limits of
LLM-driven heuristic evolution in a constrained combinatorial-optimisation
setting.

This dissertation makes three contributions. First, it delivers a working
LLM-driven evolutionary pipeline targeting the PDPTW-SE injection point,
including the technical mechanism that enables runtime code loading into
the base heuristic and the three-prompt cascade — seed, evolve, and
diversify — that drives the search. Second, it produces an empirical
characterisation of the pipeline's behaviour across a fixed evaluation
grid and five random seeds, honestly reporting where the paradigm
succeeds and where it plateaus. Third, it offers an interpretive
discussion of what the discovered heuristics reveal about the underlying
problem structure and about the paradigm's reach — including the
specific and reproducible ways in which the discovered candidates
compose the strategies the evolutionary prompts named.

Applied to the six-instance multi-island benchmark, the pipeline
produced three successive champions across sixteen generations of
full-grid evolution, exhibiting monotonically improving mean grid
fitness. All three champions decisively outperform the paper's
tightest-time-window baseline; the strongest of them beats the random
baseline on the single-seed grid and on some but not all instances
under multi-seed evaluation. The evolutionary loop reaches a plateau at
the third champion, which is confirmed as terminal across a second
eight-generation session under identical configuration. Chapter 4
reports these results in full; Chapter 5 develops what they imply for
the paradigm.

## 1.3 Contributions

## 1.4 Dissertation structure
