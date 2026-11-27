#!/usr/bin/env python3
"""24 h screen for Peters, PASTA, and REG. FDR is within cohort when that column exists."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis._scores import read_scores, rhythm_groups
from oscillation import rhythm_table


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python analysis/transcriptomic_rhythm.py scores.csv results.csv")
    df = read_scores(sys.argv[1])
    groups, family = rhythm_groups(df)
    rhythm_table(df, groups, family).to_csv(sys.argv[2], index=False)


if __name__ == "__main__":
    main()
