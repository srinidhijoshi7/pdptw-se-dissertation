# Current best champion (updated after Chat 05 run 2)
# Hash: cbbe47d2468c, fitness: 0.9681

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