T = int(input())
for test_case in range(1, T + 1):
    N = int(input())
    A = list(map(int, input().split()))
    A.sort()

    # Two smallest go to corners (1,1) and (2,N)
    corner1 = A[0]
    corner2 = A[1]
    middle = A[2:]  # 2*(N-1) values
    M = N - 1  # each group has M values

    if M == 0:
        # N=1 edge case (shouldn't happen since N>=2, but just in case)
        print(corner1)
        print(corner2)
        continue

    S_mid = sum(middle)
    target = S_mid // 2

    # Step 2: Subset sum DP with bitsets
    # dp[k] = big integer bitset where bit j is set if we can pick exactly k
    # values from middle summing to j
    # We need to pick exactly M values.
    num_vals = len(middle)  # = 2*M

    # Forward DP: process each value and update
    # dp[k] after processing i values: achievable sums using exactly k of first i values
    # For backtracking, store dp after each step
    # dp_history[i][k] = bitset after processing first i values, choosing exactly k

    # Memory optimization: we only need dp_history for backtracking
    # Store dp[k] for each stage
    dp_history = []

    dp = [0] * (M + 1)
    dp[0] = 1  # sum 0 with 0 chosen values

    dp_history.append([x for x in dp])

    for i in range(num_vals):
        v = middle[i]
        # Update dp in reverse order of k to avoid using same value twice
        for k in range(min(i + 1, M), 0, -1):
            dp[k] |= (dp[k - 1] << v)
        dp_history.append([x for x in dp])

    # Find best sum in dp[M] closest to target (but <= target preferred for balance)
    final = dp[M]
    best_sum_F = -1
    # Search outward from target
    for delta in range(S_mid + 1):
        lo = target - delta
        hi = target + delta
        if lo >= 0 and (final >> lo) & 1:
            best_sum_F = lo
            break
        if hi <= S_mid and (final >> hi) & 1:
            best_sum_F = hi
            break

    # Make sure best_sum_F <= S_mid // 2 (the smaller group)
    if best_sum_F > S_mid - best_sum_F:
        best_sum_F = S_mid - best_sum_F

    # Step 3: Backtrack to find which values belong to F
    chosen = [False] * num_vals
    remaining_sum = best_sum_F
    remaining_count = M

    for i in range(num_vals - 1, -1, -1):
        v = middle[i]
        # Check if value i was chosen: if we remove it, can we achieve
        # remaining_sum - v with remaining_count - 1 from first i values?
        if remaining_count > 0 and remaining_sum >= v:
            prev = dp_history[i][remaining_count - 1]
            if (prev >> (remaining_sum - v)) & 1:
                chosen[i] = True
                remaining_sum -= v
                remaining_count -= 1

    # chosen[] marks the group with smaller sum (best_sum_F <= S_mid/2)
    # That group goes to L (row 2, descending), the other to F (row 1, ascending)
    F = []
    L = []
    for i in range(num_vals):
        if chosen[i]:
            L.append(middle[i])
        else:
            F.append(middle[i])

    # Sort F ascending (for row 1, columns 2..N)
    F.sort()
    # Sort L ascending (for row 2, columns 1..N-1)
    L.sort()

    # Construct grid
    row1 = [corner1] + F
    row2 = L + [corner2]

    print(' '.join(map(str, row1)))
    print(' '.join(map(str, row2)))
