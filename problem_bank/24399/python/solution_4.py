import math

def main():
    T = int(input())
    for tc in range(T):
        line = input().split()
        Q = int(line[0])
        N = int(line[1])
        F = list(map(int, input().split()))
        M = sum(F)

        # Read all Q sequences into a flat list (0-indexed ball types)
        seq = [0] * (Q * M)
        idx = 0
        for q in range(Q):
            line = input().split()
            for t in range(M):
                seq[idx] = int(line[t]) - 1
                idx += 1

        # Pre-compute draw positions for each type in each experiment
        first_draw = [0] * (Q * N)
        second_draw = [0] * (Q * N)
        draw_count = [0] * N

        for q in range(Q):
            base_seq = q * M
            base_pos = q * N
            for j in range(N):
                draw_count[j] = 0
            for t in range(M):
                j = seq[base_seq + t]
                if draw_count[j] == 0:
                    first_draw[base_pos + j] = t
                else:
                    second_draw[base_pos + j] = t
                draw_count[j] += 1

        # Separate types into F=1 and F=2 groups for faster inner loop
        types_f1 = []
        types_f2 = []
        for j in range(N):
            if F[j] == 1:
                types_f1.append(j)
            else:
                types_f2.append(j)

        # MM (Minorization-Maximization) fixed-point iteration
        NUM_ITERS = 25
        W = [1.0] * N
        cumsum = [0.0] * (M + 1)

        for iteration in range(NUM_ITERS):
            denom = [0.0] * N

            S0 = 0.0
            for j in range(N):
                S0 += F[j] * W[j]

            _seq = seq
            _fd = first_draw
            _sd = second_draw
            _W = W
            _cumsum = cumsum
            _denom = denom
            _tf1 = types_f1
            _tf2 = types_f2

            for q in range(Q):
                base_seq = q * M
                base_pos = q * N

                S = S0

                cs = 0.0
                _cumsum[0] = 0.0
                for t in range(M):
                    cs += 1.0 / S
                    _cumsum[t + 1] = cs
                    S -= _W[_seq[base_seq + t]]

                for j in _tf1:
                    _denom[j] += _cumsum[_fd[base_pos + j] + 1]

                for j in _tf2:
                    bp_j = base_pos + j
                    _denom[j] += _cumsum[_fd[bp_j] + 1] + _cumsum[_sd[bp_j] + 1]

            # MM update with convergence check
            max_change = 0.0
            for i in range(N):
                new_w = Q * F[i] / denom[i]
                if W[i] > 1e-300:
                    change = abs(new_w / W[i] - 1.0)
                    if change > max_change:
                        max_change = change
                W[i] = new_w

            max_w = 0.0
            for i in range(N):
                if W[i] > max_w:
                    max_w = W[i]
            inv_max = 1.0 / max_w
            for i in range(N):
                W[i] *= inv_max

            if max_change < 1e-8:
                break

        # ===== Fisher-based James-Stein Shrinkage =====

        # Step 2: One extra pass to compute denom_sq (Fisher information)
        denom_sq = [0.0] * N
        cumsum_sq = [0.0] * (M + 1)

        S0 = 0.0
        for j in range(N):
            S0 += F[j] * W[j]

        for q in range(Q):
            base_seq = q * M
            base_pos = q * N

            S = S0

            cs = 0.0
            cumsum_sq[0] = 0.0
            cumsum[0] = 0.0
            for t in range(M):
                inv_S = 1.0 / S
                cs += inv_S * inv_S
                cumsum_sq[t + 1] = cs
                cumsum[t + 1] = cumsum[t] + inv_S
                S -= W[seq[base_seq + t]]

            for j in types_f1:
                denom_sq[j] += cumsum_sq[first_draw[base_pos + j] + 1]

            for j in types_f2:
                bp_j = base_pos + j
                denom_sq[j] += cumsum_sq[first_draw[bp_j] + 1] + cumsum_sq[second_draw[bp_j] + 1]

        # Step 3: Compute per-type variance in log space
        var = [0.0] * N
        log_w = [0.0] * N
        for i in range(N):
            fisher_i = Q * F[i] / (W[i] * W[i]) - denom_sq[i]
            if fisher_i > 1e-30:
                var[i] = 1.0 / (W[i] * W[i] * fisher_i)
            else:
                var[i] = 1.0  # large variance fallback
            if W[i] > 1e-300:
                log_w[i] = math.log(W[i])
            else:
                log_w[i] = -690.0

        # Step 4: Cluster types by proximity in log(W) space
        # Sort types by log(W)
        sorted_idx = list(range(N))
        sorted_idx.sort(key=lambda i: log_w[i])

        # Average variance
        sigma2 = 0.0
        for i in range(N):
            sigma2 += var[i]
        sigma2 /= N

        # Gap threshold
        gap_thresh = 3.0 * math.sqrt(sigma2)

        # Sequential clustering
        clusters = []
        current_cluster = [sorted_idx[0]]
        for k in range(1, N):
            if log_w[sorted_idx[k]] - log_w[sorted_idx[k - 1]] > gap_thresh:
                clusters.append(current_cluster)
                current_cluster = [sorted_idx[k]]
            else:
                current_cluster.append(sorted_idx[k])
        clusters.append(current_cluster)

        # Step 5: James-Stein shrinkage within each cluster of size >= 3
        shrunk_log_w = [0.0] * N
        for i in range(N):
            shrunk_log_w[i] = log_w[i]

        for cluster in clusters:
            nc = len(cluster)
            if nc < 3:
                continue
            # Cluster mean
            mu = 0.0
            for j in cluster:
                mu += log_w[j]
            mu /= nc
            # Sum of squares
            ss = 0.0
            for j in cluster:
                d = log_w[j] - mu
                ss += d * d
            # Shrinkage factor (positive-part James-Stein)
            # Classic JS: theta_JS = mu + max(0, 1 - (nc-2)*sigma2/ss) * (x - mu)
            if ss > 1e-30:
                shrink = 1.0 - (nc - 2) * sigma2 / ss
                if shrink < 0.0:
                    shrink = 0.0
            else:
                shrink = 0.0
            # Apply shrinkage
            for j in cluster:
                shrunk_log_w[j] = mu + shrink * (log_w[j] - mu)

        # Step 6: Convert back and normalize
        for i in range(N):
            W[i] = math.exp(shrunk_log_w[i])

        max_w = 0.0
        for i in range(N):
            if W[i] > max_w:
                max_w = W[i]
        if max_w > 0:
            inv_max = 1.0 / max_w
            for i in range(N):
                W[i] *= inv_max

        # Output: NO #T prefix, just space-separated floats
        out_parts = []
        for i in range(N):
            out_parts.append('%.15g' % W[i])
        print(' '.join(out_parts))

main()
