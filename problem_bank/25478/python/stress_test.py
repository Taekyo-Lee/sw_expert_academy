import random
import subprocess
import os

SOLUTION = os.path.join(os.path.dirname(__file__), "solution_3.py")
BRUTE = os.path.join(os.path.dirname(__file__), "brute_force.py")

def generate_random_proper_interval_graph(N, D):
    """Generate a random symmetric matrix that could be a valid proper interval graph
    communication matrix for some placement with distance D."""
    # Random approach: generate a random N x N symmetric matrix with 1s on diagonal
    # where A[i][j] = 1 means receivers i and j must be within distance D
    # We need to ensure the matrix is realizable as a proper interval graph
    # Simple approach: just generate random symmetric 0/1 matrices
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        A[i][i] = 1
    for i in range(N):
        for j in range(i + 1, N):
            A[i][j] = random.randint(0, 1)
            A[j][i] = A[i][j]
    return A

def generate_test_case():
    N = random.randint(2, 6)
    X = random.randint(N, min(N + 10, 15))
    D = random.randint(1, 4)
    A = generate_random_proper_interval_graph(N, D)
    return N, X, D, A

def format_input(cases):
    lines = [str(len(cases))]
    for N, X, D, A in cases:
        lines.append("%d %d %d" % (N, X, D))
        for row in A:
            lines.append("".join(str(x) for x in row))
    return "\n".join(lines) + "\n"

def run_solution(input_str, script):
    result = subprocess.run(
        ["python3", script],
        input=input_str,
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        return None, result.stderr
    return result.stdout.strip().split("\n"), None

def main():
    num_tests = 500
    batch_size = 50  # Run multiple cases per invocation for speed
    mismatches = 0
    total = 0

    for batch in range(num_tests // batch_size):
        cases = [generate_test_case() for _ in range(batch_size)]
        input_str = format_input(cases)

        sol_out, sol_err = run_solution(input_str, SOLUTION)
        bf_out, bf_err = run_solution(input_str, BRUTE)

        if sol_out is None:
            print("Solution error:", sol_err)
            return
        if bf_out is None:
            print("Brute force error:", bf_err)
            return

        for i in range(batch_size):
            total += 1
            if sol_out[i] != bf_out[i]:
                mismatches += 1
                N, X, D, A = cases[i]
                print("MISMATCH #%d: N=%d X=%d D=%d" % (mismatches, N, X, D))
                for row in A:
                    print("".join(str(x) for x in row))
                print("Solution: %s  Brute: %s" % (sol_out[i], bf_out[i]))
                if mismatches >= 5:
                    print("Too many mismatches, stopping.")
                    return

        if (batch + 1) % 2 == 0:
            print("Batch %d/%d done, %d tests, %d mismatches" % (batch + 1, num_tests // batch_size, total, mismatches))

    print("Done: %d tests, %d mismatches" % (total, mismatches))

if __name__ == "__main__":
    main()
