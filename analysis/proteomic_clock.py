#!/usr/bin/env python3
"""24 h screen for the Tanaka clock and any other proteomic clocks in the file."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis._scores import read_scores
from oscillation import rhythm_table


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: python analysis/proteomic_clock.py scores.csv results.csv")
    df = read_scores(sys.argv[1])
    rhythm_table(df, ["clock"]).to_csv(sys.argv[2], index=False)


if __name__ == "__main__":
    main()
