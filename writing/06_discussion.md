# Chapter 5 — Discussion

*[Target: ~2500 words. **Distinction chapter.** Synthesis over summary.]*

## 5.1 Chapter roadmap

Chapter 5 interprets the empirical results reported in Chapter 4 against the
research questions posed in Section 2.7 and against the three foundational works
of LLM-driven algorithm discovery reviewed in Section 2.6. Where Chapter 4 was
deliberately organised around reporting — numbers, tables, and structural
descriptions — Chapter 5 is organised around interpretation: the
substantive questions Chapter 4 opened but did not close.

Section 5.2 delivers the direct interpretive answers to the three
sub-questions from Section 2.7. Section 5.3 develops the methodologically novel
finding of this dissertation — the genesis of the Gen 3 champion under
the diversify prompt, and the LLM's compositional treatment of the
prompt's family menu — as a claim about the mechanism of the
three-prompt cascade this dissertation designed. Section 5.4 treats the
plateau at Gen 3 as four candidate explanations rather than one, and
refuses to pick among them without further experimental evidence.
Section 5.5 turns the persistent negative result on `lr102-10R` into an
interpretive contribution about the reach of insertion-order-based
heuristics on this problem. Section 5.6 positions the results against
FunSearch (Romera-Paredes et al., 2024), Evolution of Heuristics (Liu
et al., 2024), and ReEvo (Ye et al., 2024), stating explicitly what the
present work confirms, complicates, and lacks relative to each; the
concrete extension experiments that would relax the limitations named
there are the subject of Chapter 6.

## 5.2 Answering the research questions

The three sub-questions posed in Section 2.7 admit three distinct answers when
evaluated against the results of Chapter 4.

**RQ1 — Comparison against hand-designed baselines.** LLM-evolved candidates
outperform Barbosa, Tiwari and Melo's (2026) `tightest_tw` baseline
decisively and consistently; they outperform the `random` baseline only
partially. Under multi-seed evaluation across the six-instance grid (Table
4.2), all three champions produce a lower mean ratio than `tightest_tw`
(Gen 1: 1.0065, Gen 2: 1.0058, Gen 3: 1.0024, all against `tightest_tw`'s
1.0130). None of the three champions produces a mean ratio strictly below
1.000, however, which means none beats `random` on average across seeds.
The favourable single-seed picture reported in Section 4.3 — Gen 3 at 0.9969,
0.31% below random — is genuine at seed 17 and reproducible on a fresh
machine, but is a favourable slice rather than the seed-averaged verdict.
The honest verdict on RQ1 is: LLM evolution reliably beats a hand-designed
baseline that itself already fails to beat random on this problem, and
produces occasional single-seed improvements over random that do not
survive seed aggregation.

**RQ2 — Seed generalisation.** The improvements observed at seed 17 do not
generalise across the {17, 42, 100, 200, 500} seed grid in the sense of a
uniform per-instance improvement, but they do generalise in specific
per-instance ways that matter methodologically. Gen 3 beats `random` on
`lr103-6R` across all five seeds (mean 0.9943 ± 0.0121) and on `lr201-6R`
in mean (0.9960 ± 0.0089) — two of the six instances on which the
seed-averaged behaviour is improved. On `lr101-10R`, all
candidates including `tightest_tw` exhibit large per-seed variance
(standard deviations 0.05–0.10), with individual ratios ranging from
0.9005 to 1.1095, suggesting that MSLP at `--mslpa = 10` on this instance
is dominated by seed-sensitivity in the multi-start restarts rather than
by the initial ordering the candidates influence. On `lr102-10R`, no
champion beats `random` at any seed. The honest verdict on RQ2 is:
improvements are real but instance-specific, and the pipeline as
configured discovers champions that are seed-robust on some instances
(notably `lr103-6R`) and seed-sensitive on others.

**RQ3 — Structural characteristics of successful candidates.** The three
champions exhibit three qualitatively different construction paradigms:
Gen 1 a parallel weighted-sum scorer with a Gillett-Miller (1974) sweep
component, Gen 2 a sequential greedy chain constructor, and Gen 3 a
uniformly-selected mixture of three distinct strategies (Section 4.6). Two
observations about this progression carry interpretive weight for the
mechanism of LLM-driven heuristic evolution. First, each new champion
was structurally distinct from its parent — the LLM did not converge on a
single algorithmic family and refine it, but produced structurally
different families in successive generations. Second, the strongest
champion of the three (Gen 3, on both single-seed grid fitness and
multi-seed mean) was the one that abandoned single-strategy commitment in
favour of a probabilistic mixture. The mechanism by which the mixture
arose — the interaction between the diversify prompt and the LLM's
apparent hedging behaviour — is developed in Section 5.3. What the mixture and
the plateau together imply about the reach of the paradigm is developed
in Sections 5.4 and 5.6.

## 5.3 The diversify mechanism and the Gen 3 mixture

Three concrete observations about Gen 3's genesis carry interpretive weight
beyond the numerical results of Chapter 4. The first is that the diversify
prompt fired exactly when its design anticipated. The stagnation counter
(Section 3.5) is configured to fire when two consecutive generations produce no
improvement over the incumbent; in the full-grid run, Gen 3 emerged at
generation 3, slot 0, after generations 1 and 2 each produced offspring
that failed to beat the seeded Gen 2 champion. The diversify prompt
therefore did not fire eagerly (before genuine local exhaustion) or
tardily (long after it) — it fired precisely at the point of local
exhaustion the design was engineered around. This alignment between
design and observed behaviour is a small but concrete validation of the
stagnation-triggered prompt-switching mechanism, and is the first instance
across the sixteen generations of full-grid evolution where diversify
directly produced a winning candidate.

The second observation concerns the content of what Gen 3 produced. The
diversify prompt (Section 3.6, Appendix B) explicitly names five candidate
strategy families the LLM may draw from: lexicographic ordering,
cluster-then-order, greedy nearest-in-time, reverse-order construction,
and pair-tightness ordering. Gen 3's three mode branches (Section 4.6) implement,
respectively: cluster-then-lexicographic sorting (matching two of the
five prompted families simultaneously — cluster-then-order and
lexicographic); reverse-deadline lexicographic construction (matching
reverse-order construction); and greedy spatio-temporal nearest chain
(matching greedy nearest-in-time). Three of the five prompted families
therefore appear directly in the winning candidate. The two absent
families — pair-tightness ordering as a primary key, and pure
lexicographic sorting without a clustering step — do not appear. The
prompt's family menu was, in this instance, taken literally.

The third observation is the most methodologically interesting. The
diversify prompt asks the LLM to pick **one** family (or invent one of
comparable distinctness); it does not suggest composing multiple. Gen 3
composed three. The mixture architecture — three complete strategies,
selected by uniform random draw at every MSLP restart — was the LLM's
own initiative rather than the prompt's instruction, and it is this
mixture that beats the two single-strategy predecessors on grid fitness
and on the multi-seed mean. This connects to a design point about the
prompt cascade itself. This dissertation reduced the four-prompt
taxonomy of Evolution of Heuristics (Liu et al., 2024) to three
(seed/evolve/diversify), collapsing EoH's two exploration prompts (e1,
e2) into a single stagnation-triggered mechanism. That collapse gave up
the fine-grained control of EoH's separate exploration variants; what
this observation suggests is that a sufficiently capable proposer,
prompted with a menu of distinct families rather than a single one,
may recover that fine-grained control on its own — by composing multiple
families rather than picking one. Whether that is a general property of
LLM-driven heuristic evolution or an idiosyncrasy of `gemini-3.6-flash`
on this specific problem is beyond the scope of this dissertation.

## 5.4 The plateau and its four candidate explanations

Section 4.7 established that Gen 3 is the terminal champion of the
full-grid trajectory across sixteen generations and thirty-two evaluated
candidates, at the fixed evaluation configuration {seed 17, `--mslpa = 10`,
`gemini-3.6-flash`, λ = 2}. What determines the plateau at this specific
configuration is genuinely unclear, and four candidate explanations are
worth naming; the evidence within this dissertation distinguishes them
only partially, and the strongest defensible position is to hold all four
open rather than to pick a preferred narrative.

**Explanation 1: The (1+λ = 2) evolutionary strategy is too narrow.** With
only two offspring per generation and strict elitism, the loop's search
is aggressive on exploitation and thin on exploration; the diversify
prompt (Section 3.6) is the only structural exploration mechanism, and it fires
only after two-generation stagnation. FunSearch (Romera-Paredes et al.,
2024) samples on the order of millions of candidates across parallel
islands, and EoH (Liu et al., 2024) uses populations an order of
magnitude larger than two. The plateau may reflect a search-budget
insufficiency rather than a mechanism failure. This dissertation cannot
directly distinguish this from the alternatives below, because the
Gemini free-tier quota (Section 3.7) precludes running with larger λ across
enough generations to test the hypothesis adequately.

**Explanation 2: The `gemini-3.6-flash` model has reached a capability
ceiling on this problem.** The prompt cascade (Section 3.6) provides increasingly
targeted guidance across seed, evolve, and diversify variants, yet the
extension session's diversify candidates in generations 9–16 produced
neither Gen-3-level fitness nor structural approaches beyond what
generations 1–8 had already explored. If the LLM's reachable design space
for insertion-scoring functions on the PDPTW-SE is bounded by the model's
pretraining exposure to relevant algorithmic literature, the plateau may
reflect that bound. Testing this requires running the pipeline with a
higher-capability model on the same problem, which was outside this
dissertation's scope (Section 3.7).

**Explanation 3: The `--mslpa = 10` evaluation harness masks the
discriminative signal.** Section 3.4 justified the choice of ten restarts
on the grounds that higher values (piloted at 100) collapse the fitness
signal to three discrete points. Ten restarts restore sensitivity to
ordering, but the surviving signal is small — most Chapter 4 ratios sit
within ±3% of 1.000. If further improvements require an ordering that
strongly differentiates itself from the semi-greedy random selections
already made across the ten restarts, `--mslpa = 10` may lack the
resolution to reward candidates that would improve at, say, five restarts
or a different mix of construction budget and LP-improvement budget.
Testing this requires a dedicated sweep of restart budgets at fixed
candidates, which was outside the compute budget of this dissertation.

**Explanation 4: The six-instance grid lacks the structural diversity to
reward further exploration.** Table 4.2 shows that four of the six
instances (`lr101-6R`, `lr102-6R`, `lr201-6R`, `lr102-10R`) admit only
narrow-band ratios around 1.000 for every candidate tested; two
(`lr103-6R`, `lr101-10R`) show meaningful movement. If mean-ratio fitness
on this grid is effectively determined by candidate performance on those
two instances, the evolutionary loop has an implicit sample size of two,
not six — and a search plateau under such a fitness signal is not
surprising. Testing this requires expanding the grid to include
multi-floor (Type 2) instances and larger request counts, which is
future work (Chapter 6).

The four explanations are not mutually exclusive; more likely the plateau
reflects some combination of all four. The interpretive stance this
dissertation takes is deliberate: rather than pick the most convenient
explanation, it names the space of candidate mechanisms and identifies
the extension experiments needed to distinguish them. Those extensions
are the substance of Chapter 6's future work.

## 5.5 The lr102-10R persistent negative

On `lr102-10R`, no champion beats `random` at any of the five evaluation
seeds. The `tightest_tw` baseline also loses on this instance, and by the
largest margin of any baseline-instance pair in the grid (mean 1.0455,
Table 4.2). Every non-`random` service-order configuration tested in this
dissertation — one hand-designed rule and three LLM-evolved candidates,
spanning parallel weighted-sum scoring, sequential greedy chain
construction, and probabilistic mixtures of three distinct strategies —
produces a worse expected outcome than a uniform random permutation on
this instance. This is a striking pattern, and its interpretation is
narrower than it may first appear.

The pattern most naturally reads as evidence about the class of methods
to which every configuration tested belongs, rather than evidence against
any specific configuration within it. All five candidates — the two
baseline rules and the three LLM-evolved champions — impose a
deterministic-plus-perturbation ordering on the pickup requests before
the semi-greedy insertion phase begins. `random`, by contrast, imposes no
prior structure at all, leaving the semi-greedy insertion's own
α-controlled restricted-candidate-list selection (Section 3.2) to construct the
ordering implicitly through its per-restart choices. If `lr102-10R` has
structural features that make any prior ordering worse in expectation
than a purely random one — for instance, if its request geometry is such
that adjacent-in-ordering requests tend to have incompatible time
windows, so imposed orderings systematically produce insertion sequences
the LP-improvement phase (Section 3.2) cannot recover from — then the failure
mode is intrinsic to the family of insertion-order-based heuristics, not
to the specific orderings within it. The LLM did not fail to find a
better ordering on `lr102-10R`; there may not be one to find, within the
family of methods it was asked to search over.

This is a real limitation of the paradigm as instantiated here, and it
matters both for reporting and for extension. For reporting, it must be
named as a limitation and not obscured — no champion universally beats
`random` on the grid, and the reason is not stochastic noise but a
specific instance on which the entire method class underperforms
`random`. For extension, it suggests that a natural direction for this
line of work is not another prompt-cascade refinement or a larger
evolutionary budget but an injection point outside the initial-ordering
family — for example, evolving a ruin-and-recreate operator inside a
large-neighbourhood-search wrapper, where the LLM's contribution would
determine which requests to remove and which to reinsert. That extension
sits outside the scope of the present dissertation and is developed as
future work in Chapter 6.

## 5.6 Position against FunSearch, EoH, ReEvo, and honest limitations

This dissertation applies the paradigm of LLM-driven evolutionary program
search — established by FunSearch (Romera-Paredes et al., 2024) and
extended by Evolution of Heuristics (Liu et al., 2024) and ReEvo (Ye et
al., 2024) — to a problem the paradigm has not previously been tested on:
the Pickup and Delivery Problem with Time Windows and Scheduling on the
Edges, introduced by Barbosa, Tiwari and Melo (2026). The results of
Chapter 4 admit specific relational claims against each of the three
landmarks — what they confirm, what they complicate, and where the
present study falls short.

Against FunSearch, the results provide a modest confirmation of the
core mechanism's generalisability. FunSearch showed that a pretrained
code LLM coupled with a systematic evaluator can advance the state of
the art on established open problems, primarily in domains — cap-set
lower bounds, online bin packing — where the evaluator returns a binary
or narrow-band correctness signal and the program's role is compact and
combinatorially interpretable. The present work shows the same
generator-plus-gatekeeper mechanism producing meaningful ordering
functions in a much richer combinatorial setting — integer scheduling
constraints, machine-synchronisation edges, and a mixed-region topology
— under a fitness signal that is continuous rather than binary and an
evaluator that is itself stochastic. That the mechanism produces
monotonically improving grid fitness across three generations and a
structurally novel mixture-of-strategies champion (Section 4.6, Section 5.3) is
evidence that the FunSearch paradigm extends beyond the compact-program
settings in which it was first demonstrated. The confirmation is modest 
because the compute scale here — sixteen generations, thirty-two candidates, 
gemini-3.6-flash on a twenty-request-per-day free-tier quota — is roughly four 
orders of magnitude smaller than the sampling regime FunSearch operated under. 
What the paradigm can achieve at FunSearch-scale compute on PDPTW-SE remains an 
open question this dissertation cannot address.

Against EoH, the results complicate the implicit population-size claim
and add a specific empirical observation about prompt-cascade design.
EoH argued for co-evolving natural-language thoughts and executable code
under a four-prompt taxonomy (e1, e2, m1, m2) with populations
substantially larger than the (1+λ = 2) strategy used here, and
demonstrated sample-efficiency gains against FunSearch on bin packing.
The present work reduced EoH's four-prompt taxonomy to three
(seed/evolve/diversify) and used a population of two, and hit a plateau
after sixteen generations that EoH's larger populations might have
escaped. Whether the plateau is attributable to population size,
prompt-cascade coarseness, model capability, or evaluation-harness
saturation is exactly the ambiguity Section 5.4 refuses to resolve. What the
present work adds is a specific observation Section 5.3 already developed: the
diversify prompt's family menu was, in the Gen 3 case, treated by the
LLM as a compositional palette rather than a selection list — three of
the five named families appeared as branches of a single mixture
candidate. Whether this compositional behaviour is a general property of
sufficiently capable proposers or an idiosyncrasy of `gemini-3.6-flash`
on this problem is the natural question to investigate at larger scale.

Against ReEvo, the present work does not implement the reflection
mechanism that ReEvo introduced — a separate "reflector" LLM that
compares parent heuristics in natural language and distils long-term
design hints — and its absence is the most direct account of what the
present pipeline lacks. The diversify prompt (Section 3.6) provides a form of
structured exploration relaunch but does not accumulate long-horizon
reasoning across generations; the loop's memory extends only to the
current champion and its immediate fitness. A ReEvo-style reflection
layer, added between the champion display and the offspring generation
step, would be a natural extension and might address the plateau
Explanation 1 of Section 5.4 identifies. Beyond the missing reflection layer,
this dissertation is bounded by four honest limitations: it evaluates
only one LLM (`gemini-3.6-flash`), on one problem (PDPTW-SE, and only
its multi-island Type 1 instances of ≤ 10 requests), at one restart
budget (`--mslpa = 10`), under one prompt-cascade design (three prompts,
menu-of-five diversify families). Chapter 6 develops the specific
extension experiments that would relax each of these bounds.