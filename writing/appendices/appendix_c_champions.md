# Appendix C — Champion Julia Source Code

This appendix reproduces the source code of the three LLM-evolved
champions referenced from Section 4.2 and structurally characterised in
Section 4.6. All three files are archived in the project repository at
`src/python/llm_loop/champions/` under the content-hash-tagged
filenames shown below. Each file carries a metadata header giving its
generation index, content hash, evaluation configuration, per-instance
fitness values, LLM model, and parent hash; the code that follows the
header is the exact source that was `include`d into the Multistart
module at evaluation time via the `LLM_CANDIDATE_FILE` environment
variable and the `Base.invokelatest` dispatch mechanism described in
Section 3.3.

The three champions define a monotonic single-seed grid-fitness
progression at seed 17: Gen 1 at 1.0024, Gen 2 at 0.9993, Gen 3 at
0.9969 (Table 4.1). Under multi-seed evaluation the progression holds
for Gen 1 → Gen 2 → Gen 3 at 1.0065 → 1.0058 → 1.0024 respectively
(Table 4.2). Section 4.6 develops the structural characterisation of each
in prose; this appendix supplies the underlying code for
reproducibility and audit.

## C.1 Gen 1 — parallel weighted-sum scorer with sweep component

Gen 1 (content hash `d1791ed1796e`) was the first LLM-generated
candidate in this dissertation's experimental record to achieve a
fitness value below 1.0000. It emerged at generation 1, slot 0, from
the evolve prompt in an initial dev-mode run on the `lr101-10R`
instance at seed 17, λ = 2, and `--mslpa = 10`. Structurally it is a
parallel weighted-sum scorer with per-restart weight sampling: seven
features are extracted per pickup request (earliest pickup time, pair
slack, pickup-to-delivery Euclidean distance, cross-region flag,
pickup demand, region coordinate, sweep angle around the instance
centroid with randomly-sampled phase), min-max normalised, and
combined into a scalar score via a weighted linear sum with eight
random weights sampled uniformly per MSLP restart. The sweep-angle
component is the classical Gillett and Miller (1974) sweep heuristic,
adapted from capacitated vehicle routing by using the pickup centroid
in place of a depot.

**Source file:** `src/python/llm_loop/champions/first_beat_random_d1791ed1796e.jl`

```julia
# First LLM candidate to beat random baseline
# Instance: lr101 10R (10R_10V_02I_04M/t1/lr101)
# Seed: 17,  --mslpa: 10
# Baseline (random): 1297.54
# This candidate:    1265.95
# Fitness (ratio):   0.9757
# Improvement:       2.43%
# Model: gemini-3.6-flash
# Timestamp: 2026-08-06T21:05:51.846555+00:00
# Code hash: d1791ed1796e

function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    n = inst.n
    if n <= 1
        return Vector{Int64}(inst.V_p)
    end

    ep = Vector{Float64}(undef, n)
    slack = Vector{Float64}(undef, n)
    dist = Vector{Float64}(undef, n)
    cross = Vector{Float64}(undef, n)
    dem = Vector{Float64}(undef, n)
    floor_v = Vector{Float64}(undef, n)
    sweep = Vector{Float64}(undef, n)

    sum_x = 0.0
    sum_y = 0.0
    @inbounds for k in 1:n
        p = inst.V_p[k]
        jp = inst.jobs[p]
        sum_x += Float64(jp.point.x)
        sum_y += Float64(jp.point.y)
    end
    cx = sum_x / Float64(n)
    cy = sum_y / Float64(n)

    phi = 2.0 * pi * rand(params.rng)

    @inbounds for k in 1:n
        p = inst.V_p[k]
        d = inst.V_d[k]

        jp = inst.jobs[p]
        jd = inst.jobs[d]

        ep[k] = Float64(inst.e[p])
        slack[k] = Float64(inst.l[d] - inst.e[p])

        dx = Float64(jp.point.x - jd.point.x)
        dy = Float64(jp.point.y - jd.point.y)
        dist[k] = sqrt(dx * dx + dy * dy)

        cross[k] = (jp.point.z != jd.point.z) ? 1.0 : 0.0
        dem[k] = Float64(inst.q[p])
        floor_v[k] = Float64(jp.point.z)

        ang = atan(Float64(jp.point.y) - cy, Float64(jp.point.x) - cx) - phi
        sweep[k] = mod(ang, 2.0 * pi) / (2.0 * pi)
    end

    norm_vec! = (arr::Vector{Float64}) -> begin
        mn = minimum(arr)
        mx = maximum(arr)
        rng_val = mx - mn
        if rng_val > 1e-9
            @inbounds for i in 1:length(arr)
                arr[i] = (arr[i] - mn) / rng_val
            end
        else
            fill!(arr, 0.0)
        end
    end

    norm_vec!(ep)
    norm_vec!(slack)
    norm_vec!(dist)
    norm_vec!(cross)
    norm_vec!(dem)
    norm_vec!(floor_v)

    w_ep = rand(params.rng) * 2.0
    w_slack = rand(params.rng) * 2.0
    w_sweep = rand(params.rng) * 2.5
    w_dist = rand(params.rng) * 1.5
    w_dem = rand(params.rng) * 1.5
    w_cross = rand(params.rng) * 1.5
    w_floor = rand(params.rng) * 1.0
    noise_w = rand(params.rng) * 0.35

    scores = Vector{Float64}(undef, n)
    @inbounds for k in 1:n
        scores[k] = w_ep * ep[k] +
                    w_slack * slack[k] +
                    w_sweep * sweep[k] +
                    w_floor * floor_v[k] -
                    w_dist * dist[k] -
                    w_dem * dem[k] -
                    w_cross * cross[k] +
                    noise_w * rand(params.rng)
    end

    perm = sortperm(scores)
    result = Vector{Int64}(undef, n)
    @inbounds for k in 1:n
        result[k] = Int64(inst.V_p[perm[k]])
    end

    return result
end
```

## C.2 Gen 2 — sequential greedy chain constructor

Gen 2 (content hash `cbbe47d2468c`) was produced in a subsequent
dev-mode session seeded from Gen 1 via the champion-seed mechanism
(Section 3.5), with the remaining configuration identical (lr101-10R,
seed 17, λ = 2, `--mslpa = 10`). It emerged at generation 1, slot 1,
from the evolve prompt — *not* from diversify. Structurally, Gen 2
departs from Gen 1's parallel scoring in every respect except the
function signature: coordinates and time windows are extracted per
request, instance-level normalisation scales for distance and time are
computed, four random weights are sampled per restart (space, time,
region, slack), and the ordering is then built sequentially by
one-step lookahead — at each step selecting the unvisited request that
minimises a weighted cost combining distance from the previous
request's pickup or delivery to the next pickup, a region-change
penalty, a time-gap term, a remaining-slack term, and a small uniform
jitter. The starting pickup is selected as the earliest-`e_p` request
with probability 0.3 and uniformly at random otherwise.

**Source file:** `src/python/llm_loop/champions/gen2_cbbe47d2468c.jl`

```julia
# Second-generation LLM champion
# Parent: d1791ed1796e (yesterday's champion, fitness 0.9757)
# This candidate: cbbe47d2468c, fitness 0.9681
# Instance: lr101 10R,  seed 17,  --mslpa 10
# Baseline (random): 1297.54
# This candidate cost: 1256.16
# Improvement over random: 3.19%
# Improvement over gen-1 champion: 0.76%
# Model: gemini-3.6-flash
# Timestamp: 2026-08-08T13:37:42.991017+00:00
# Generation: 1,  Slot: 1
# Parent hash: d1791ed1796e

function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    n = inst.n
    if n <= 1
        return Vector{Int64}(inst.V_p)
    end

    px = Vector{Float64}(undef, n)
    py = Vector{Float64}(undef, n)
    pz = Vector{Int64}(undef, n)
    dx = Vector{Float64}(undef, n)
    dy = Vector{Float64}(undef, n)
    dz = Vector{Int64}(undef, n)
    ep = Vector{Float64}(undef, n)
    ld = Vector{Float64}(undef, n)

    min_x = Inf
    max_x = -Inf
    min_y = Inf
    max_y = -Inf
    min_e = Inf
    max_l = -Inf

    @inbounds for k in 1:n
        p = inst.V_p[k]
        d = inst.V_d[k]

        jp = inst.jobs[p]
        jd = inst.jobs[d]

        px[k] = Float64(jp.point.x)
        py[k] = Float64(jp.point.y)
        pz[k] = Int64(jp.point.z)

        dx[k] = Float64(jd.point.x)
        dy[k] = Float64(jd.point.y)
        dz[k] = Int64(jd.point.z)

        ep[k] = Float64(inst.e[p])
        ld[k] = Float64(inst.l[d])

        min_x = min(min_x, px[k], dx[k])
        max_x = max(max_x, px[k], dx[k])
        min_y = min(min_y, py[k], dy[k])
        max_y = max(max_y, py[k], dy[k])

        min_e = min(min_e, ep[k])
        max_l = max(max_l, ld[k])
    end

    scale_dist = max(1.0, sqrt((max_x - min_x)^2 + (max_y - min_y)^2))
    scale_time = max(1.0, max_l - min_e)

    w_space = 0.5 + rand(params.rng) * 1.0
    w_time  = 0.5 + rand(params.rng) * 1.0
    w_floor = 1.0 + rand(params.rng) * 2.0
    w_slack = 0.2 + rand(params.rng) * 0.8

    visited = fill(false, n)
    order = Vector{Int64}(undef, n)

    if rand(params.rng) < 0.3
        best_e = Inf
        start_k = 1
        @inbounds for k in 1:n
            if ep[k] < best_e
                best_e = ep[k]
                start_k = k
            end
        end
        order[1] = start_k
    else
        order[1] = rand(params.rng, 1:n)
    end
    visited[order[1]] = true

    @inbounds for step in 2:n
        prev = order[step - 1]
        best_k = -1
        best_cost = Inf

        for k in 1:n
            if !visited[k]
                d1 = sqrt((px[k] - px[prev])^2 + (py[k] - py[prev])^2)
                d2 = sqrt((px[k] - dx[prev])^2 + (py[k] - dy[prev])^2)
                d_sp = min(d1, d2) / scale_dist

                f_pen = (pz[k] != pz[prev] && pz[k] != dz[prev]) ? 1.0 : 0.0

                t_gap = max(0.0, ep[k] - ep[prev]) / scale_time
                t_diff = abs(ep[k] - ep[prev]) / scale_time

                slack = (ld[k] - ep[k]) / scale_time

                cost = w_space * d_sp +
                       w_floor * f_pen +
                       w_time * (0.7 * t_gap + 0.3 * t_diff) +
                       w_slack * slack +
                       0.05 * rand(params.rng)

                if cost < best_cost
                    best_cost = cost
                    best_k = k
                end
            end
        end

        order[step] = best_k
        visited[best_k] = true
    end

    result = Vector{Int64}(undef, n)
    @inbounds for k in 1:n
        result[k] = Int64(inst.V_p[order[k]])
    end

    return result
end
```

## C.3 Gen 3 — three-way probabilistic mixture

Gen 3 (content hash `dacd3ec6f6c7`) was produced in a third session
with the evolutionary loop reconfigured to compute fitness as the mean
ratio across all six instances of the grid (MODE = full), seeded from
Gen 2 via the champion-seed mechanism, at seed 17, λ = 2,
`--mslpa = 10`. It emerged at generation 3, slot 0, from the
**diversify** prompt after two consecutive stagnation generations
under evolve — the first and only occasion across the sixteen
generations of full-grid evolution reported in Section 4.7 on which
the diversify mechanism directly produced a winning candidate.
Structurally, Gen 3 is a probabilistic mixture of three distinct
construction strategies selected by uniform random draw at every
MSLP restart:

- with probability 0.50, a **cluster-then-lexicographic sort**:
  pickups are keyed by a six-tuple whose leading components group
  by pickup region and prioritise cross-region requests, tight pair
  slack, and early pickups;
- with probability 0.25, a **reverse-deadline lexicographic sort**:
  the key inverts the sign of the latest-delivery time, then the
  latest-pickup time, then the pair slack, ordering the tightest-
  deadline requests first;
- with probability 0.25, a **greedy spatio-temporal nearest chain**
  whose structure mirrors Gen 2's chain constructor but replaces the
  weighted-sum cost with a strict three-tuple lexicographic key
  (region change, time gap, distance).

Three of the five families named in the diversify prompt (Section 3.6,
Appendix B.3) — lexicographic ordering, cluster-then-order, and
greedy nearest-in-time — appear directly in the three branches; the
prompt named the families as alternatives to select from, and the
LLM treated them as a compositional palette. The methodological
significance of this behaviour is developed in Section 5.3.

**Source file:** `src/python/llm_loop/champions/gen3_dacd3ec6f6c7.jl`

```julia
# Third-generation LLM champion — full-grid optimised
# Ancestor: cbbe47d2468c (Chat 05 champion, single-instance optimised)
# This candidate: dacd3ec6f6c7, grid fitness 0.9969
# Optimised on: all 6 instances (MODE=full), seed 17, --mslpa 10
# Model: gemini-3.6-flash
# Generation: 3, Slot: 0, Prompt kind: diversify
# Parent hash: cbbe47d2468c
#
# Per-instance ratios (< 1.0 = beats random on that instance):
#   06R_06V_02I_04M/t1/lr101: 1.0000
#   06R_06V_02I_04M/t1/lr102: 1.0000
#   06R_06V_02I_04M/t1/lr103: 0.9989
#   06R_06V_02I_04M/t2/lr201: 1.0000
#   10R_10V_02I_04M/t1/lr101: 0.9744
#   10R_10V_02I_04M/t1/lr102: 1.0082
#
function llm_candidate_score(inst::InstanceData, params::ParameterData)::Vector{Int64}
    n = inst.n
    if n <= 1
        return Vector{Int64}(inst.V_p)
    end

    mode_val = rand(params.rng)

    if mode_val < 0.50
        # Strategy 1: Cluster-then-Lexicographic Hardness Sorting
        # Group by pickup island (z), prioritizing cross-island requests, tight pair slack, and early pickups
        keys = Vector{Tuple{Int64, Int64, Float64, Float64, Float64, Float64}}(undef, n)

        @inbounds for k in 1:n
            p = inst.V_p[k]
            d = inst.V_d[k]

            jp = inst.jobs[p]
            jd = inst.jobs[d]

            p_z = Int64(jp.point.z)
            d_z = Int64(jd.point.z)

            cross_island = (p_z != d_z) ? 0 : 1
            pair_slack = Float64(inst.l[d] - inst.e[p])
            earliest_p = Float64(inst.e[p])

            dx = Float64(jp.point.x - jd.point.x)
            dy = Float64(jp.point.y - jd.point.y)
            dist = sqrt(dx * dx + dy * dy)

            jitter = rand(params.rng) * 1e-4

            keys[k] = (p_z, cross_island, pair_slack, earliest_p, -dist, jitter)
        end

        perm = sortperm(keys)

        result = Vector{Int64}(undef, n)
        @inbounds for k in 1:n
            result[k] = Int64(inst.V_p[perm[k]])
        end
        return result

    elseif mode_val < 0.75
        # Strategy 2: Reverse-Deadline Lexicographic Construction
        # Process requests backwards starting from latest delivery deadline and window tightness
        keys = Vector{Tuple{Float64, Float64, Float64, Float64}}(undef, n)

        @inbounds for k in 1:n
            p = inst.V_p[k]
            d = inst.V_d[k]

            latest_d = Float64(inst.l[d])
            latest_p = Float64(inst.l[p])
            pair_slack = Float64(inst.l[d] - inst.e[p])
            jitter = rand(params.rng) * 1e-4

            keys[k] = (-latest_d, -latest_p, -pair_slack, jitter)
        end

        perm = sortperm(keys)

        result = Vector{Int64}(undef, n)
        @inbounds for k in 1:n
            result[k] = Int64(inst.V_p[perm[k]])
        end
        return result

    else
        # Strategy 3: Greedy Spatio-Temporal Nearest Chain
        # Build sequential chain using strict lexicographic priority on floor changes, time gaps, and distances
        px = Vector{Float64}(undef, n)
        py = Vector{Float64}(undef, n)
        pz = Vector{Int64}(undef, n)
        dx = Vector{Float64}(undef, n)
        dy = Vector{Float64}(undef, n)
        dz = Vector{Int64}(undef, n)
        ep = Vector{Float64}(undef, n)
        ld = Vector{Float64}(undef, n)

        @inbounds for k in 1:n
            p = inst.V_p[k]
            d = inst.V_d[k]

            jp = inst.jobs[p]
            jd = inst.jobs[d]

            px[k] = Float64(jp.point.x)
            py[k] = Float64(jp.point.y)
            pz[k] = Int64(jp.point.z)

            dx[k] = Float64(jd.point.x)
            dy[k] = Float64(jd.point.y)
            dz[k] = Int64(jd.point.z)

            ep[k] = Float64(inst.e[p])
            ld[k] = Float64(inst.l[d])
        end

        visited = fill(false, n)
        order = Vector{Int64}(undef, n)

        best_e = Inf
        start_k = 1
        @inbounds for k in 1:n
            score = ep[k] + rand(params.rng) * 2.0
            if score < best_e
                best_e = score
                start_k = k
            end
        end

        order[1] = start_k
        visited[start_k] = true

        @inbounds for step in 2:n
            prev = order[step - 1]
            best_k = 1
            best_key = (Inf, Inf, Inf)

            for k in 1:n
                if !visited[k]
                    floor_change = (pz[k] == dz[prev] || pz[k] == pz[prev]) ? 0.0 : 1.0
                    time_gap = max(0.0, ep[k] - ld[prev])
                    dist = sqrt((px[k] - dx[prev])^2 + (py[k] - dy[prev])^2) + rand(params.rng) * 1e-3

                    key = (floor_change, time_gap, dist)
                    if key < best_key
                        best_key = key
                        best_k = k
                    end
                end
            end

            order[step] = best_k
            visited[best_k] = true
        end

        result = Vector{Int64}(undef, n)
        @inbounds for k in 1:n
            result[k] = Int64(inst.V_p[order[k]])
        end
        return result
    end
end
```

## C.4 Provenance summary

The three champions form the parent-lineage `d1791ed1796e →
cbbe47d2468c → dacd3ec6f6c7`, with the parent hash recorded in each
file's metadata header and additionally in the `candidates.jsonl`
and `generations.jsonl` logs archived under `logs/archive/`. All
three files are byte-identical to the versions used in the multi-seed
evaluation of Table 4.2 and the plateau-extension of Section 4.7 and
Table 4.3. The single-seed grid results of Table 4.1 can be
reproduced by installing each champion in turn as the
`LLM_CANDIDATE_FILE` and invoking `src/julia/run_champions.sh`, which
takes approximately twenty minutes on the reference hardware
(Section 3.7).