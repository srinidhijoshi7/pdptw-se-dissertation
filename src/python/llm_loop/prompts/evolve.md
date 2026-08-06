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