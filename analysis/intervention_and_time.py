#!/usr/bin/env python3
"""Matched-hour intervention contrast, and a daytime-versus-night contrast in the control arm.

Also writes the 24 h fit inside each condition.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis._scores import read_scores
from oscillation import matched_hour_contrast, rhythm_table, time_of_day_contrast


def main():
    p = argparse.ArgumentParser()
    p.add_argument("scores")
    p.add_argument("results")
    p.add_argument("--intervention", required=True)
    p.add_argument("--control", required=True)
    p.add_argument("--day", type=float, default=None)
    p.add_argument("--night", type=float, default=None)
    args = p.parse_args()

    df = read_scores(args.scores)
    parts = []

    matched = matched_hour_contrast(df, args.intervention, args.control)
    matched.insert(0, "test", "matched_hour")
    parts.append(matched)

    if args.day is not None and args.night is not None:
        tod = time_of_day_contrast(df, args.day, args.night, control=args.control)
        tod.insert(0, "test", "time_of_day")
        parts.append(tod)

    fit = rhythm_table(df, ["condition", "clock"], family=["condition"])
    fit.insert(0, "test", "cosinor")
    parts.append(fit)
    pd.concat(parts, ignore_index=True).to_csv(args.results, index=False)


if __name__ == "__main__":
    main()
