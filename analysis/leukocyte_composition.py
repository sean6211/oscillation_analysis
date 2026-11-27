#!/usr/bin/env python3
"""Retest clocks after residualizing cell fractions, or compare discrete hours.

cell_* columns are fractions. compartment splits mixed blood from purified cells.
--timepoints 0,6,30 compares each later hour with the first (Jiang PBMCs).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis._scores import read_scores
from oscillation import rhythm_table, time_of_day_contrast


def _cell_columns(frame: pd.DataFrame) -> list[str]:
    return [column for column in frame.columns if column.startswith("cell_")]


def _residualize(frame: pd.DataFrame, cell_columns: list[str]) -> pd.DataFrame:
    pieces = []
    covariates = " + ".join(cell_columns)
    for clock, clocks in frame.groupby("clock", dropna=False):
        use = clocks.dropna(subset=["value", "participant", *cell_columns]).copy()
        if use["participant"].nunique() < 2 or len(use) < 4:
            continue
        fit = smf.ols(f"value ~ {covariates} + C(participant)", use).fit()
        use = use.copy()
        use["value"] = fit.resid
        pieces.append(use)
    if not pieces:
        return frame.iloc[0:0].copy()
    return pd.concat(pieces, ignore_index=True)


def _timepoints(frame: pd.DataFrame, hours: list[float]) -> pd.DataFrame:
    first, rest = hours[0], hours[1:]
    marked = frame.copy()
    marked["condition"] = "timepoint"
    return pd.concat(
        [time_of_day_contrast(marked, later, first, control="timepoint") for later in rest],
        ignore_index=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scores")
    parser.add_argument("results")
    parser.add_argument("--timepoints", default=None, help="comma-separated hours, for example 0,6,30")
    args = parser.parse_args()
    frame = read_scores(args.scores)

    if args.timepoints:
        hours = [float(item) for item in args.timepoints.split(",") if item.strip()]
        if len(hours) < 2:
            raise SystemExit("--timepoints needs at least two hours")
        _timepoints(frame, hours).to_csv(args.results, index=False)
        return

    pieces = []
    if "compartment" in frame.columns:
        pieces.append(rhythm_table(frame, ["compartment", "clock"], family=["compartment"]))
    else:
        pieces.append(rhythm_table(frame, ["clock"]))

    cell_columns = _cell_columns(frame)
    if cell_columns:
        residual = _residualize(frame, cell_columns)
        adjusted = rhythm_table(residual, ["clock"])
        adjusted.insert(0, "adjustment", "cell_fraction")
        pieces.append(adjusted)
    pd.concat(pieces, ignore_index=True).to_csv(args.results, index=False)


if __name__ == "__main__":
    main()
