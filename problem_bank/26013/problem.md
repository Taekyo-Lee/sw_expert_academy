# 26013. 비숍 (Bishop)

- **Difficulty:** D7 (VH)
- **Point:** 200
- **Accuracy**: 25.0%

## Constraints

- **Time:** 50 test cases combined — C: 1s / C++: 20s / Java: 30s / Python: 30s
- **Memory:** Heap + static: 256MB, Stack: 1MB

## Problem Description

체스판에서 비숍이라는 말은 같은 대각선상에 있는 말을 공격할 수 있는 말이다.

n × n 체스판에 k 개의 비숍을 놓아서, 모든 비숍이 다른 칸에 존재하며, 어떠한 비숍도 다른 비숍을 공격할 수 없게끔 하는 배정을 평화로운 배정이라고 하자.

모든 1 ≤ k ≤ 2n-1 에 대해서 평화로운 배정의 개수를 998244353으로 나눈 나머지를 출력하라.

## Input

첫 번째 줄에 테스트 케이스의 수 TC가 주어진다.

이후 TC개의 테스트 케이스가 새 줄로 구분되어 주어진다.

각 테스트 케이스는 다음과 같이 구성되었다.

- 첫 번째 줄에 정수 N 이 주어진다. (1 ≤ N ≤ 100000)

## Output

각각의 테스트 케이스 마다 2n-1 개의 정수로 k = 1, k = 2, …, k = 2n-1 일 때의 답을 순서대로 출력하라.

각 정수는 하나의 공백으로 구분하여 출력한다. 마지막 정수 끝에 공백이 붙어서는 안 된다.

**Note:** This problem does NOT use the `#N` prefix in the output format.

## Sample

### Input

```
3
1
2
6
```

### Output

```
1
4 4 0
36 520 3896 16428 39680 53744 38368 12944 1600 64 0
```

## Sample Explanation

- **N=1:** 1×1 board, k=1: only 1 way to place 1 bishop. Output: `1`
- **N=2:** 2×2 board, k can be 1,2,3 (2×2-1=3): Output: `4 4 0`
- **N=6:** 6×6 board, k can be 1..11 (2×6-1=11): Output: `36 520 3896 16428 39680 53744 38368 12944 1600 64 0`
