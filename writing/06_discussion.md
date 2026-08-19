# Chapter 5 — Discussion

*[Target: ~2500 words. **Distinction chapter.** Synthesis over summary.]*

## 5.1 Chapter roadmap

*[To be written last, after §§5.2–5.6 exist.]*

## 5.2 Answering the research questions

The three sub-questions posed in §2.7 admit three distinct answers when
evaluated against the results of Chapter 4.

**RQ1 — Comparison against hand-designed baselines.** LLM-evolved candidates
outperform Barbosa, Tiwari and Melo's (2026) `tightest_tw` baseline
decisively and consistently; they outperform the `random` baseline only
partially. Under multi-seed evaluation across the six-instance grid (Table
4.2), all three champions produce a lower mean ratio than `tightest_tw`
(Gen 1: 1.0065, Gen 2: 1.0058, Gen 3: 1.0024, all against `tightest_tw`'s
1.0130). None of the three champions produces a mean ratio strictly below
1.000, however, which means none beats `random` on average across seeds.
The favourable single-seed picture reported in §4.3 — Gen 3 at 0.9969,
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
seed-averaged behaviour is genuinely improved. On `lr101-10R`, all
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
uniformly-selected mixture of three distinct strategies (§4.6). Two
observations about this progression carry interpretive weight for the
mechanism of LLM-driven heuristic evolution. First, each new champion
was structurally distinct from its parent — the LLM did not converge on a
single algorithmic family and refine it, but produced meaningfully
different families in successive generations. Second, the strongest
champion of the three (Gen 3, on both single-seed grid fitness and
multi-seed mean) was the one that abandoned single-strategy commitment in
favour of a probabilistic mixture. The mechanism by which the mixture
arose — the interaction between the diversify prompt and the LLM's
apparent hedging behaviour — is developed in §5.3. What the mixture and
the plateau together imply about the reach of the paradigm is developed
in §§5.4 and 5.6.

## 5.3 The diversify mechanism and the Gen 3 mixture

Three concrete observations about Gen 3's genesis carry interpretive weight
beyond the numerical results of Chapter 4. The first is that the diversify
prompt fired exactly when its design anticipated. The stagnation counter
(§3.5) is configured to fire when two consecutive generations produce no
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
diversify prompt (§3.6, Appendix B) explicitly names five candidate
strategy families the LLM may draw from: lexicographic ordering,
cluster-then-order, greedy nearest-in-time, reverse-order construction,
and pair-tightness ordering. Gen 3's three mode branches (§4.6) implement,
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

*[Section to follow.]*

## 5.5 The lr102-10R persistent negative

*[Section to follow.]*

## 5.6 Position against FunSearch, EoH, ReEvo, and honest limitations

*[Section to follow.]*