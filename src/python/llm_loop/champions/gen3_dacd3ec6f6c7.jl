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