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

*[Section to follow.]*

## 5.4 The plateau and its four candidate explanations

*[Section to follow.]*

## 5.5 The lr102-10R persistent negative

*[Section to follow.]*

## 5.6 Position against FunSearch, EoH, ReEvo, and honest limitations

*[Section to follow.]*