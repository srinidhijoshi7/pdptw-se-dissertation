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

The remainder of this dissertation is organised into six chapters.

Chapter 2 reviews the two literatures at whose intersection this
dissertation sits: the long-established body of work on the pickup and
delivery problem with time windows and its variants — including the
PDPTW-SE — and the recent literature on LLM-driven evolutionary
program search for algorithm discovery. The chapter closes by
identifying the specific gap this dissertation fills and by mapping
that gap onto the injection point the pipeline targets.

Chapter 3 describes the experimental pipeline in full. It sets out the
Multi-Start LP-Improvement heuristic that serves as the base method,
the technical mechanism by which LLM-generated candidates are injected
into it at runtime, the fitness harness and evaluation grid, the (1+λ)
evolutionary loop that drives generation, the three-prompt cascade
that varies the LLM's role across the search, and the model
configuration and reproducibility artefacts that make the results
replayable.

Chapter 4 reports the empirical findings. It presents the three
champions the pipeline produced, their comparison against the two
hand-designed baselines at a fixed evaluation seed and across a wider
seed grid, per-instance analysis of the two most methodologically
significant anomalies (a breakthrough instance and a persistent
negative one), a structural characterisation of the three champion
Julia functions, and a plateau-confirmation extension in which a
second evolutionary session produced no further improvement.

Chapter 5 interprets those findings against the research questions
posed in Chapter 2 and against the three foundational works of
LLM-driven algorithm discovery reviewed there. It delivers the direct
answers to the sub-questions, develops the methodological finding
about the diversify prompt's role in producing the third champion,
treats the observed plateau as four candidate explanations rather
than one, argues that the persistent negative on a specific instance
reflects a limitation of the family of insertion-order-based methods
rather than of the pipeline specifically, and states explicitly what
this work confirms, complicates, and lacks relative to prior work in
the field.

Chapter 6 summarises the contributions, restates the answers to the
research questions in compact form, and identifies the concrete
extension experiments that would relax the limitations named in
Chapter 5. An abstract, ethics documentation, prompt templates, and
champion source code are provided in appendices.

## 1.4 Dissertation structure

Three points about the presentation of this work are worth stating at
the outset.

First, the reporting-versus-interpretation split between Chapters 4
and 5 is deliberate. Chapter 4 is organised around empirical
reporting: numbers, tables, structural descriptions, and the two
figures that make the central patterns visible. It is disciplined
about not editorialising, and it defers every substantive
interpretation to Chapter 5. Chapter 5 in turn is organised entirely
around interpretation — answering the research questions, explaining
the methodologically significant findings, treating limitations
honestly, and positioning the results against prior work in the
field. A reader interested in what happened experimentally can read
Chapter 4 alone; a reader interested in what those experiments imply
for the paradigm should read Chapters 4 and 5 together.

Second, the dissertation is intended to be reproducible. The pipeline
described in Chapter 3 is committed to a private Git repository
alongside every candidate the evolutionary loop produced, every
generation log, and every result artefact used to construct the
tables and figures. The central reproduction — the three-champion
comparison of Chapter 4 — takes approximately twenty minutes to
regenerate from a fresh clone with only Julia and Gurobi installed;
setup and reproduction instructions accompany the code.

Third, the study is a computational one using publicly available
secondary benchmark data; no human participants, primary data
collection, or personally identifying information are involved.
Ethical framing, including the approval history and the disclosure
of large-language-model usage during code generation, is set out in
full in Section 3.8, and the approval documentation is included in
Appendix A.