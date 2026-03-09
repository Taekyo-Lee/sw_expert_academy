"""Generate a synthetic test case for problem 24399.

Creates Q=30000 experiments with N=30 types, known weights.
Outputs:
  - tests/synthetic_input.txt  (the input file)
  - tests/true_weights.txt     (the true weights for validation)
"""

import random
import os

random.seed(42)

Q = 30000
N = 30
M = 30  # sum of F_i = 30

# Generate F_i: N types, each F_i in {1, 2}, sum = 30
# With N=30, all F_i=1 gives sum=30, or some can be 2
# Let's use all F_i = 1 for simplicity
F = [1] * N

# Generate weights: mix of scenarios
# Scenario: roughly uniform with some variation
# Use weights that create clusters to test the shrinkage
true_W = [0.0] * N
# Group 1 (indices 0-9): weight ~ 1.0
for i in range(10):
    true_W[i] = 1.0
# Group 2 (indices 10-19): weight ~ 0.5
for i in range(10, 20):
    true_W[i] = 0.5
# Group 3 (indices 20-29): weight ~ 0.2
for i in range(20, 30):
    true_W[i] = 0.2

# Normalize so max = 1
max_w = max(true_W)
for i in range(N):
    true_W[i] /= max_w

# Generate experiments
experiments = []
for q in range(Q):
    # Current counts
    counts = list(F)
    draw_order = []
    for t in range(M):
        # Compute probabilities
        total = 0.0
        for j in range(N):
            total += counts[j] * true_W[j]
        # Draw
        r = random.random() * total
        cum = 0.0
        chosen = N - 1
        for j in range(N):
            cum += counts[j] * true_W[j]
            if cum > r:
                chosen = j
                break
        draw_order.append(chosen + 1)  # 1-indexed
        counts[chosen] -= 1
    experiments.append(draw_order)

# Write input file
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'synthetic_input.txt'), 'w') as f:
    f.write('1\n')
    f.write('%d %d\n' % (Q, N))
    f.write(' '.join(str(x) for x in F) + '\n')
    for exp in experiments:
        f.write(' '.join(str(x) for x in exp) + '\n')

# Write true weights
with open(os.path.join(script_dir, 'true_weights.txt'), 'w') as f:
    f.write(' '.join('%.15g' % w for w in true_W) + '\n')

print("Generated synthetic_input.txt (%d experiments, %d types)" % (Q, N))
print("True weights:", ' '.join('%.4f' % w for w in true_W))
