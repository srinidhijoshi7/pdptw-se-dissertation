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