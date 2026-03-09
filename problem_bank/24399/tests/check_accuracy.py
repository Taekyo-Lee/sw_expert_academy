"""Check pairwise ratio accuracy of solution output vs true weights."""

import os

script_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(script_dir, 'true_weights.txt')) as f:
    true_w = list(map(float, f.read().split()))

with open(os.path.join(script_dir, 'synthetic_output.txt')) as f:
    est_w = list(map(float, f.read().split()))

N = len(true_w)
assert len(est_w) == N, "Mismatch: %d vs %d" % (len(est_w), N)

max_err = 0.0
worst_pair = (0, 0)

for i in range(N):
    for j in range(N):
        if true_w[i] <= true_w[j]:
            true_ratio = true_w[i] / true_w[j]
            est_ratio = est_w[i] / est_w[j]
            err = abs(est_ratio - true_ratio)
            if err > max_err:
                max_err = err
                worst_pair = (i, j)

print("N = %d" % N)
print("Max pairwise ratio error: %.6f" % max_err)
print("Worst pair: (%d, %d)" % worst_pair)
i, j = worst_pair
print("  True: W[%d]/W[%d] = %.6f / %.6f = %.6f" % (i, j, true_w[i], true_w[j], true_w[i]/true_w[j]))
print("  Est:  W[%d]/W[%d] = %.6f / %.6f = %.6f" % (i, j, est_w[i], est_w[j], est_w[i]/est_w[j]))
print()

if max_err < 0.02:
    print("PASS: max error %.6f < 0.02 threshold" % max_err)
else:
    print("FAIL: max error %.6f >= 0.02 threshold" % max_err)

# Also show per-group stats
for name, indices in [("Group 1 (w=1.0)", range(10)), ("Group 2 (w=0.5)", range(10,20)), ("Group 3 (w=0.2)", range(20,30))]:
    vals = [est_w[i] for i in indices]
    avg = sum(vals) / len(vals)
    mn = min(vals)
    mx = max(vals)
    print("  %s: avg=%.6f min=%.6f max=%.6f spread=%.6f" % (name, avg, mn, mx, mx-mn))
