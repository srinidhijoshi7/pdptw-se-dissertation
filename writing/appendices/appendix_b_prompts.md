# Appendix B — Prompt Templates

This appendix reproduces in full the three prompt templates that
constitute the three-prompt cascade described in Section 3.6: `seed`,
`evolve`, and `diversify`. Each prompt targets a distinct role in the
evolutionary loop — seeding generation zero from scratch, refining the
current champion in non-stagnating generations, and requesting a
structurally different candidate when the search stagnates. Together
they operationalise the collapse of the four-prompt taxonomy of
Evolution of Heuristics (Liu et al., 2024) into three prompts, as
justified in Section 3.6.

All three prompts share a common substrate: a natural-language
description of the PDPTW-SE, a functional specification of the required
Julia function (name, argument types, return type), a documented layout
of the `InstanceData` and `Job` structs the candidate may read, and a
`Common failure modes to avoid` section drawn from pilot-run failures.
Where the three prompts diverge is in their **task framing**: the seed
prompt asks the LLM to construct a scoring function from scratch, the
evolve prompt injects the current champion's source code and fitness
and asks for a refinement, and the diversify prompt injects the same
champion metadata but instructs the LLM to abandon the champion's
family and select from a named menu of five alternative strategy
families. Template variables in the evolve and diversify prompts are
denoted by `{{DOUBLE_BRACES}}` and are substituted by the Python driver
at each generation.

The prompts are committed at `src/python/llm_loop/prompts/` in the
project repository and are the canonical version at commit hash
`d1791ed1796e` and subsequent. They are reproduced here verbatim for
audit-clean documentation of the exact instructions given to the LLM.

## B.1 Seed prompt

The seed prompt fires only at generation zero, and only when no
champion-seed file is present (Section 3.5). Its role is to elicit a first
compilable candidate from the LLM with no reference to any previous
attempt. The prompt therefore contains no template variables; its
content is identical across every fresh run.

**Source file:** `src/python/llm_loop/prompts/seed.md` (102 lines)

````markdown
# Task

You are designing a heuristic component for the **Pickup and Delivery Problem with Time Windows and Scheduling on the Edges (PDPTW-SE)**.

Specifically, you must implement the **service order function** used inside a multi-start greedy insertion heuristic. This function decides the order in which pickup requests are processed by the greedy insertion phase. A good ordering leads to better initial solutions and, ultimately, lower-cost final solutions after local search.

## Context

- The problem: a fleet of vehicles serves pickup–delivery request pairs across multiple islands, subject to hard time windows and edge scheduling constraints (ferries between islands).
- The heuristic: multi-start greedy insertion, repeated ~100 times with different orderings; the best solution across restarts is kept.
- Your target: the ordering function. Two existing baselines are `random` (uniform random permutation) and `tightest_tw` (sort by tightness of time window `l_i − e_i`, tightest first). Empirically, `random` beats `tightest_tw` on this problem.

## The interface

You must implement exactly this function in Julia:

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # your implementation
end
```

## Available data — EXACT field names

**`inst::InstanceData`:**
- `inst.n`                : `Int` — number of pickup requests
- `inst.V_p`              : `Vector{Int}` — pickup node indices (length n)
- `inst.V_d`              : `Vector{Int}` — delivery node indices, paired positionally with V_p
- `inst.e[i]`             : `Float64` — earliest service time at node i
- `inst.l[i]`             : `Float64` — latest service time at node i
- `inst.q[i]`             : `Int` — demand at node i (positive for pickup, negative for delivery)
- `inst.jobs[i]`          : a `Job` struct (see below)

**`Job` struct fields:**
- `.id::Int64`      — job identifier
- `.point::Point`   — spatial location (see below)
- `.dem::Int64`     — demand
- `.earl::Int64`    — earliest service time
- `.lat::Int64`     — latest service time
- `.servt::Int64`   — service time
- `.pid::Int64`     — for deliveries: the id (NOT the node index) of the paired pickup Job. For pickups: 0.
- `.did::Int64`     — for pickups: the id (NOT the node index) of the paired delivery Job. For deliveries: 0.

**CRITICAL — pairing:** `.pid` and `.did` are external Job IDs from the instance file, **NOT indices into `inst.jobs`**. To pair pickup `p = inst.V_p[k]` with its delivery **node index**, use `d = inst.V_d[k]`. Do NOT write `inst.jobs[job.did]` — that will crash with a BoundsError.

Example — correct pairing:
```julia
for k in 1:inst.n
    p = inst.V_p[k]         # pickup node index (safe for inst.jobs, inst.e, inst.l)
    d = inst.V_d[k]         # paired delivery node index (safe for same)
    # ... use p and d
end
```

**`Point` struct fields:**
- `.x::Int64`  — x coordinate
- `.y::Int64`  — y coordinate
- `.z::Int64`  — z coordinate (island / floor identifier — NOT called `.floor`)

**`params::ParameterData`:**
- `params.rng` — a `Random.MersenneTwister` you can use for reproducible randomness (call `rand(params.rng, ...)`)

Access example:
```julia
p = inst.V_p[k]                     # pickup index
xp = inst.jobs[p].point.x           # its x coordinate
zp = inst.jobs[p].point.z           # its z coordinate (island)
tw_width = inst.l[p] - inst.e[p]    # its time window width
```

## Constraints

- Return a `Vector{Int64}` — a permutation of the pickup indices in `inst.V_p`.
- The returned vector must have length `inst.n`.
- Every value must be a valid pickup node index (element of `inst.V_p`).
- No duplicates.
- The file will be `include`d into an existing module. **Do NOT define any function, macro, type, struct, or top-level `const` other than `llm_candidate_score` itself.** Any helper computation must be a nested closure inside `llm_candidate_score`, or better, inlined.
- Do NOT `import`, `using`, or `include` anything. `sortperm`, `sort`, `shuffle`, `rand`, `extrema`, `minimum`, `maximum`, arithmetic and array operations are all available without imports.
- Do NOT use `hasproperty`, `getfield`, or any reflection. The field names above are the ground truth — use them directly. Guessing = crash.
- Use `params.rng` for any randomness so runs are reproducible.

## Common failure modes to avoid

Real candidates on this task have failed for these specific reasons — do not repeat them:

1. **Defining helper functions at file scope** (outside `llm_candidate_score`). This causes world-age errors. Nest any helper inside the main function as a closure, or inline it.
2. **Guessing field names** with `hasproperty(job, :pos)`, `hasproperty(job, :floor)`, etc. Use the exact fields listed above.
3. **Fallback-to-random** as the dominant strategy. If your function's high-probability branch is `scores[k] = rand(params.rng)`, you have not designed a heuristic — you've built a random baseline in disguise. Commit to a deterministic-plus-perturbation strategy.
4. **Fallback-to-natural-order** as an escape hatch. Returning `copy(inst.V_p)` or `inst.V_p[1:n]` unmodified, or having an early-return that yields the input order without meaningful reordering, is a hedge — it delegates the ordering decision to whatever order the instance file happens to use. Do not use `return copy(inst.V_p)` as a fallback; commit to your chosen ordering.
5. **Wrong return type.** The dispatcher expects `Vector{Int64}`. `Vector{Any}`, tuples, or index-into-`1:n` (rather than into `inst.V_p`) will fail.
6. **Modifying `inst.V_p` in place.** It's the shared pickup list; sort a copy, or use `sortperm` and index.

## Output format

Return **only** the Julia code for `llm_candidate_score`, wrapped in a fenced code block:

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # ...
end
```

No prose, no explanation before or after the code block. Just the function.
````

## B.2 Evolve prompt

The evolve prompt fires in every non-stagnating generation from the
first onward. Its role is to condition candidate generation on the
current champion's source code and fitness value, following the
best-shot conditioning strategy of FunSearch (Romera-Paredes et al.,
2024). Two template variables are substituted at each generation:
`{{BEST_CODE}}` receives the current champion's full source code, and
`{{BEST_FITNESS}}` receives its mean-ratio grid fitness value. The
prompt closes with an anti-fallback clause prohibiting cosmetic
resubmission of the champion and, in particular, prohibiting the
weighted-sum-of-normalised-features pattern the champion likely
already uses.

**Source file:** `src/python/llm_loop/prompts/evolve.md` (91 lines)

````markdown
# Task

You are designing a heuristic component for the **Pickup and Delivery Problem with Time Windows and Scheduling on the Edges (PDPTW-SE)**.

Specifically, you must implement the **service order function** used inside a multi-start greedy insertion heuristic. This function decides the order in which pickup requests are processed by the greedy insertion phase.

## Context

- Baselines: `random` (uniform permutation) and `tightest_tw` (sort by TW width `l_i − e_i`, tightest first). Empirically `random` beats `tightest_tw`.
- The multi-start heuristic runs ~100 restarts per instance and keeps the best solution.

## Current best candidate

Below is the best `llm_candidate_score` function found so far.

**Fitness metric:** mean of (candidate_cost / random_baseline_cost) across the evaluation instances. Lower is better. **1.0 = equivalent to random. Below 1.0 = beats random.**

Current champion fitness: **{{BEST_FITNESS}}**

```julia
{{BEST_CODE}}
```

## Your task

Write a **new, meaningfully different** `llm_candidate_score` function that you believe will achieve a **lower** fitness score than the champion above.

Guidance:
- If the champion's fitness is close to 1.0, it is likely functioning as a random baseline in disguise. Your job is to **commit to a deterministic strategy**, not to re-invent randomness.
- Consider using structural information: floor/island (`.point.z`) membership, spatial clusters, delivery deadlines, request pairing.
- Consider non-linear combinations: lexicographic ordering, tiered scoring, greedy-nearest-neighbour construction, or a small deterministic base ordering perturbed by `params.rng`.
- Do NOT resubmit the champion with cosmetic changes.
- Avoid the champion's dominant pattern (do not just build a bigger weighted sum, or a bigger mode switch, if that's what it already does).

## The interface

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # your implementation
end
```

## Available data — EXACT field names

**`inst::InstanceData`:**
- `inst.n`                : `Int` — number of pickup requests
- `inst.V_p`              : `Vector{Int}` — pickup node indices (length n)
- `inst.V_d`              : `Vector{Int}` — delivery node indices, paired positionally with V_p
- `inst.e[i]`             : `Float64` — earliest service time at node i
- `inst.l[i]`             : `Float64` — latest service time at node i
- `inst.q[i]`             : `Int` — demand at node i (positive for pickup, negative for delivery)
- `inst.jobs[i]`          : a `Job` struct (see below)

**`Job` struct fields:**
- `.id::Int64`, `.point::Point`, `.dem::Int64`, `.earl::Int64`, `.lat::Int64`, `.servt::Int64`, `.pid::Int64`, `.did::Int64`

**CRITICAL — pairing:** `.pid` and `.did` are external Job IDs from the instance file, **NOT indices into `inst.jobs`**. To pair pickup `p = inst.V_p[k]` with its delivery **node index**, use `d = inst.V_d[k]`. Do NOT write `inst.jobs[job.did]` — that will crash with a BoundsError.

**`Point` struct fields:**
- `.x::Int64`, `.y::Int64`, `.z::Int64` (z is island/floor — NOT called `.floor`)

**`params::ParameterData`:**
- `params.rng` — `Random.MersenneTwister` — use `rand(params.rng, ...)`

## Constraints

- Return `Vector{Int64}` — a permutation of pickups in `inst.V_p`, length `inst.n`, no duplicates.
- Do NOT define any function, macro, type, struct, or top-level `const` other than `llm_candidate_score` itself. Nested closures inside the main function are fine but usually unnecessary.
- Do NOT `import`, `using`, or `include` anything.
- Do NOT use `hasproperty`, `getfield`, or reflection. Use the field names listed above directly.
- Use `params.rng` for any randomness.

## Common failure modes to avoid

1. Defining helper functions at file scope.
2. Guessing field names with `hasproperty`.
3. Falling back to `rand(params.rng)` as the dominant branch — that gives you the random baseline, not an improvement.
4. Returning `copy(inst.V_p)` (or the input order unmodified) as an early-return or fallback — that delegates ordering to the instance file's implicit order. Commit to your strategy.
5. Returning the wrong type (not `Vector{Int64}`) or the wrong indices (values not in `inst.V_p`).
6. Modifying `inst.V_p` in place.

## Output format

Return **only** the Julia code, wrapped in one fenced block:

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # ...
end
```

No prose before or after.
````

## B.3 Diversify prompt

The diversify prompt replaces the evolve prompt in any generation where
the stagnation counter has reached `STAGNATION_THRESHOLD = 2` (Section 3.5).
Its role is to force structural departure from the current champion:
the champion's source code is shown for reference only, and the LLM is
explicitly instructed not to build on it. In place of a refinement
directive, the prompt names five candidate strategy families the LLM
may draw from — lexicographic, cluster-then-order, greedy nearest-in-time,
reverse-order construction, and pair-tightness ordering — and asks the
LLM to commit deterministically to one (or to invent a genuinely distinct
alternative). Three template variables are substituted at each firing:
`{{BEST_CODE}}` and `{{BEST_FITNESS}}` as in the evolve prompt, plus
`{{STAGNATION_GENS}}` recording how many consecutive stagnation
generations preceded the firing. The compositional response Gen 3
exhibited to this menu — implementing three of the five families as
branches of a single probabilistic mixture — is the subject of Section 5.3.

**Source file:** `src/python/llm_loop/prompts/diversify.md` (63 lines)

````markdown
# Task

You are designing a heuristic component for the **Pickup and Delivery Problem with Time Windows and Scheduling on the Edges (PDPTW-SE)**.

Specifically, you must implement the **service order function** used inside a multi-start greedy insertion heuristic.

## Situation — stagnation

The current best strategy has stagnated at fitness **{{BEST_FITNESS}}** for {{STAGNATION_GENS}} generations. Its structure is shown below for reference **only** — do not build on it. Your job is to write something structurally different.

```julia
{{BEST_CODE}}
```

## Your task

Write a `llm_candidate_score` function using a **structurally different family** of strategy from the champion. Pick ONE of the following families (or invent your own genuinely distinct approach) and commit to it deterministically. **Do not do weighted sums of normalised features** unless you can motivate them clearly, since that's the family the champion likely already uses.

**Suggested distinct families:**

- **Lexicographic ordering** — pick a primary sort key (e.g. earliest pickup time), tie-break by a secondary key (e.g. latest delivery time), tie-break again by a tertiary key. No weighted sums; strict priority.
- **Cluster-then-order** — group pickups by island (`.point.z`), by spatial region, or by TW overlap; then within each group order by some criterion; then interleave or concatenate the groups.
- **Greedy nearest-in-time** — start with the pickup that has the earliest time window; then repeatedly pick the pickup whose earliest time is closest to the last-picked pickup's latest time.
- **Reverse-order construction** — start from the last delivery deadline and work backwards; the resulting ordering may reveal structure the forward heuristics miss.
- **Pair-tightness ordering** — for each pickup, compute the tightness of its (pickup, delivery) pair jointly (e.g. `l_d - e_p` = maximum-possible-slack for the pair); order by this joint metric.

## The interface

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # your implementation
end
```

## Available data — EXACT field names

**`inst::InstanceData`:**
- `inst.n`, `inst.V_p`, `inst.V_d`, `inst.e[i]`, `inst.l[i]`, `inst.q[i]`, `inst.jobs[i]`

**`Job` fields:** `.id`, `.point`, `.dem`, `.earl`, `.lat`, `.servt`, `.pid`, `.did`

**CRITICAL — pairing:** `.pid` and `.did` are external Job IDs from the instance file, **NOT indices into `inst.jobs`**. To pair pickup `p = inst.V_p[k]` with its delivery **node index**, use `d = inst.V_d[k]`. Do NOT write `inst.jobs[job.did]` — that will crash.

**`Point` fields:** `.x`, `.y`, `.z` (z is island/floor)

**`params.rng`** — `Random.MersenneTwister` for reproducible randomness.

## Constraints

- Return `Vector{Int64}` — permutation of `inst.V_p`, length `inst.n`, no duplicates.
- Do NOT define any function, macro, type, struct, or top-level `const` other than `llm_candidate_score`.
- Do NOT `import`, `using`, or `include`.
- Do NOT use `hasproperty`, `getfield`, or reflection.
- Use `params.rng` for any randomness — but keep the strategy fundamentally deterministic. Randomness should only perturb, not dominate.

## Output format

Return **only** the Julia code, in one fenced block. No prose.

```julia
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    # ...
end
```
````

## B.4 Prompt cascade summary

The Python driver selects which prompt to send at each generation based
on the loop state, as described in Section 3.5 and Section 3.6. The selection rule
is deterministic and depends only on (i) whether a champion-seed file
is present at run-start, and (ii) the current value of the stagnation
counter. The four resulting cases are summarised in the table below.

| Loop state                                                          | Prompt fired | Notes                                                 |
|---------------------------------------------------------------------|--------------|-------------------------------------------------------|
| Generation 0, no champion-seed file present                         | seed         | Gen 0 champion generated from scratch                 |
| Generation 0, champion-seed file present                            | (none)       | Seeded champion loaded directly, prompt bypassed      |
| Generation ≥ 1, stagnation counter < `STAGNATION_THRESHOLD` (= 2)   | evolve       | Refine champion; `{{BEST_CODE}}` and `{{BEST_FITNESS}}` substituted |
| Generation ≥ 1, stagnation counter ≥ `STAGNATION_THRESHOLD` (= 2)   | diversify    | Force structural departure; all three template variables substituted |

The stagnation counter increments in every generation that fails to
improve the champion and resets on any generation that does. It
continues to accumulate across diversify firings, so repeated
stagnation triggers repeated diversification until the champion is
improved. Across the sixteen generations of full-grid evolution
reported in Section 4.7, the diversify prompt fired at generation 3
(directly producing the Gen 3 champion) and at six further points in
the plateau-confirmation extension.