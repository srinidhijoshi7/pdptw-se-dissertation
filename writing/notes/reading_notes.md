# Reading Notes

Skim notes for each paper as I read it during dissertation writing.
Kept in git so the reading trail is part of the record.

---
---

## §2.6 drafting checklist (for tomorrow morning)

Section target: ~550 words, 5 paragraphs.

**¶1 — Opening.** Already drafted. Paradigm setup: LLM + fitness loop = automated algorithm design. Signposts three foundational works.

**¶2 — FunSearch (¬150 words). YOUR NEXT DRAFT.**
Beats to hit:
- Romera-Paredes et al. (2024), Nature — founding paper
- Four ingredients: pretrained code LLM, systematic evaluator, island-based evolution, best-shot prompting
- Conceptual pivot: evolves programs (not solutions)
- Two demonstrations: cap-set lower bound (2.2180 → 2.2202, biggest in 20 years) + bin-packing heuristics beating first/best-fit
- Significance: first verifiable novel result from LLM system on an open problem; outputs are interpretable code

**¶3 — Evolution of Heuristics (~130 words). SKIM PAPER FIRST.**
Skim Liu et al. 2024. When you skim, look specifically for:
- Their prompt operators (they name them e1, e2, m1, m2 — what does each do?)
- What they change relative to FunSearch
- Their target problems (which combinatorial optimisation benchmarks?)
Then draft. Frame EoH as the direct methodological ancestor of your seed/evolve/diversify cascade.

**¶4 — ReEvo (~100 words). SKIM PAPER FIRST.**
Skim Ye et al. 2024. Look for:
- What "reflection" means in their loop
- Where reflection sits in the flow (before or after fitness eval?)
- What benchmarks they run
Frame it as a refinement — reflection closes part of the gap between human iterative design and machine-driven design.

**¶5 — Gap statement (~80 words). NO NEW READING.**
Beats:
- Common thread across three works: fitness-driven evolution over LLM-generated code
- Applications so far: pure math (FunSearch), bin packing, some VRP benchmarks (ReEvo)
- No published application to PDPTW-SE, which was introduced Jan 2026 (Barbosa/Tiwari/Melo)
- Signpost §2.7 for full positioning
