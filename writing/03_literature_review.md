# Chapter 2 — Literature Review

*[Target: ~2500–3500 words. See notes/ch2_outline.md for section-by-section plan.]*

## 2.1 Introduction

## 2.2 The Pickup and Delivery Problem with Time Windows

## 2.3 PDPTW variants and the Scheduling-on-Edges extension

## 2.4 Metaheuristics and hyper-heuristics for combinatorial optimisation

## 2.5 Machine learning for combinatorial optimisation

## 2.6 Large language models for algorithm discovery
     The founding work of this paradigm, FunSearch (Romera-Paredes et al., 2024), showed that a pretrained code LLM paired with a systematic evaluator can advance the state of the art on established open problems, in both pure mathematics and combinatorial optimisation. Its conceptual pivot is to evolve short programs that generate solutions rather than the solutions themselves, since structured problems admit far more compact program-level descriptions than raw enumerations. Four ingredients drive the loop: a frozen LLM as proposer, an evaluator that discards incorrect outputs, an island-based population that preserves diversity across sub-groups, and best-shot prompting, in which the highest-scoring programs are fed back into the LLM's context as few-shot examples. Applied to the cap set problem, FunSearch improved the asymptotic lower bound on cap set capacity from 2.2180 to 2.2202 — the largest improvement in two decades — while a parallel bin-packing demonstration produced heuristics that beat first-fit and best-fit and generalised to instances larger than those seen in training. Because outputs are readable code rather than opaque numerical objects, researchers can inspect discovered programs for structural insight, extracting verifiable knowledge from the search.
## 2.7 Positioning of this work
