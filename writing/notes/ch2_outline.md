# Chapter 2 Outline (Literature Review)

Target: ~2,800 words. Six substantive sections plus intro. Each section
positions the reader closer to the specific gap this dissertation
addresses: no application of LLM-driven heuristic evolution to
PDPTW-SE's insertion-scoring problem.

## §2.1 Introduction (~150 words)

Roadmap paragraph: what the chapter covers, in what order, and why
each section builds toward the gap.

## §2.2 The Pickup and Delivery Problem with Time Windows (~500 words)

Anchor citations:
- Dumas, Desrosiers, Soumis (1991) — original PDPTW formulation
- Savelsbergh, Sol (1995) — the General Pickup and Delivery Problem
- Solomon (1987) — VRPTW; the benchmark family your instances derive from
- Lenstra, Rinnooy Kan (1981) — complexity of routing/scheduling
- Berbeglia et al. (2010), Parragh, Doerner, Hartl (2008) — surveys
- Ropke, Cordeau (2009) — branch-and-cut-and-price for exact PDPTW

Argument arc: define PDPTW, explain what makes it hard, establish
that exact methods scale poorly, motivate heuristic approaches.

## §2.3 PDPTW variants and the Scheduling-on-Edges extension (~600 words)

Anchor citations:
- Ghilas, Demir, Van Woensel — PDPTW with scheduled lines (closest
  structural cousin to PDPTW-SE)
- Drexl — Synchronization in Vehicle Routing survey
- Meisel & Kopfer — synchronized routing of active/passive transport
- Mourad et al. — integrating autonomous delivery
- Soriano et al. — two-region multi-depot P&D
- Curtois et al. — LNS with guided ejection for P&D
- **Barbosa, Tiwari, Melo (2026, EJOR)** — PDPTW-SE, MSLP, benchmarks.
  Dedicated subsection at the end of §2.3; the paper this extends.

Argument arc: PDPTW has grown many variants involving synchronisation,
transfers, and shared transport. PDPTW-SE unifies these ideas into an
integrated routing-and-scheduling formulation.

## §2.4 Metaheuristics and hyper-heuristics for combinatorial optimisation (~500 words)

Anchor citations (SEARCH NEEDED):
- Ropke, Pisinger (2006) — ALNS foundational. NOT YET IN ZOTERO.
- Burke et al. (2013) — Hyper-heuristics survey. NOT YET IN ZOTERO.
- Curtois et al., Ropke, Cordeau (already have) — as PDPTW examples

Argument arc: metaheuristics are the practical tool for large-scale
routing. Hyper-heuristics automate heuristic design. LLM-driven
evolution is the newest member of that family.

## §2.5 Machine learning for combinatorial optimisation (~450 words)

Anchor citations:
- Bengio, Lodi, Prouvost (2021) — ML for CO methodological tour d'horizon.
  Move from folder 04 to folder 03.
- Kool, van Hoof, Welling (2019) — Attention for routing. Move from
  folder 04 to folder 03.
- Vinyals, Fortunato, Jaitly (2015) OR Nazari et al. (2018) — one of
  these for the pointer-net / RL-routing lineage. NOT YET IN ZOTERO.

Argument arc: neural approaches to routing preceded LLM approaches.
Attention/RL produce policies; LLM-driven approaches produce algorithms.
Different levels of the stack — set up the contrast.

## §2.6 Large language models for algorithm discovery (~550 words)

Anchor citations:
- Romera-Paredes et al. (2024, Nature) — FunSearch. Foundational method
  paper. Extended treatment.
- Liu et al. (2024) — Evolution of Heuristics. Direct methodological
  ancestor of this dissertation.
- Ye et al. (2024) — ReEvo: LLMs as Hyper-Heuristics with Reflective
  Evolution.

Argument arc: FunSearch established the paradigm; EoH refined it for
optimisation; ReEvo added self-reflection. No published application to
PDPTW-SE. This is the immediate research gap.

## §2.7 Positioning of this work (~200 words)

Explicit gap statement:
- No prior application of FunSearch/EoH to PDPTW-SE
- The `get_service_order` dispatcher inside MSLP is a natural
  minimal-modification injection point identified by both the author
  and Barbosa, Tiwari, Melo (2026) as the mechanism controlling
  insertion order
- Contribution: apply the LLM-driven evolutionary paradigm to that
  specific injection point; characterise results across multiple
  seeds; interpret the empirical plateau

Cross-refs to Chapter 3 (methodology) and Chapter 4 (results).

## Coverage summary

| Section | Ready? | Papers needed |
|---|---|---|
| §2.2 Foundations | Yes | 0 |
| §2.3 Variants + PDPTW-SE | Yes | 0 |
| §2.4 Metaheuristics | No | 2 (Ropke ALNS, Burke hyper-heuristics) |
| §2.5 ML for CO | Partial | 1 (Vinyals or Nazari) |
| §2.6 LLMs for algorithm design | Yes | 0 |
| §2.7 Positioning | Yes | 0 |

## Drafting order

1. §2.6 LLMs for algorithm discovery (most exciting; warm up voice)
2. §2.2 PDPTW foundations (most classical; easy to get right)
3. §2.3 Variants + PDPTW-SE (bridge section; has Sunil's paper)
4. §2.5 ML for CO (after Zotero moves + Vinyals/Nazari search)
5. §2.4 Metaheuristics (after ALNS + Burke search)
6. §2.7 Positioning (written last, once other sections have shape)
7. §2.1 Introduction (written after §2.7)

Momentum builds from strongest coverage to weakest.
