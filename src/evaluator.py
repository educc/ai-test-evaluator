#!/usr/bin/env python3
import fileinput
import sys

from pathlib import Path

GOLD = [
    "Q1: 2025-01-31",
    "Q2: $2,200,000.00",
    "Q3: CZ-799",
    "Q4: 25MB",
    "Q5: I don't know",
    "Q6: No",
    "Q7: Evelyn Reed",
    "Q8: $1,870,000.00",
    "Q9: General Data Protection Regulation",
    "Q10: 3",
    "Q11: Signal",
    "Q12: Voice notes",
    "Q13: 100",
    "Q14: I don't know",
    "Q15: 15%",
    "Q16: $1,620,000.00",
]

def levenshtein(a: str, b: str) -> int:
    n, m = len(a), len(b)
    if n == 0: return m
    if m == 0: return n
    prev = list(range(m + 1))
    for i, ca in enumerate(a, 1):
        curr = [i] + [0] * m
        for j, cb in enumerate(b, 1):
            curr[j] = min(
                curr[j - 1] + 1,         # insertion
                prev[j] + 1,             # deletion
                prev[j - 1] + (ca != cb) # substitution
            )
        prev = curr
    return prev[m]

def match_line(line_pair: tuple[str, str]):
    line, gold_line = line_pair
    total_dist = levenshtein(line, gold_line)
    max_dist = len(max(line, gold_line))
    score = 0.0 if total_dist >= max_dist else (1 - (total_dist / max_dist)) * 100.0
    if score < 100:
        # Some extra punishment for a mismatch.
        score = score / 2
        print(f"Mismatch in:\n\t- {gold_line}\n\t+ {line}")
    return score

def main():
    name = "Stdin (unkown)"
    if len(sys.argv) > 1:
        name = Path(sys.argv[1]).stem
        print("Evaluating:", name)
    lines = [ln.rstrip("\n") for ln in fileinput.input()]
    non_empty = [ln.strip() for ln in lines if ln.strip()][-len(GOLD):]
    scores = list(map(match_line, zip(non_empty, GOLD)))
    score = sum(scores) / len(scores)
    print(f"{name} scored: {score:.2f}")

if __name__ == "__main__":
    main()
