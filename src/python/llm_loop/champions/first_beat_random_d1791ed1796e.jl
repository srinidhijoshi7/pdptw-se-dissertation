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