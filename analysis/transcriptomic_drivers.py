#!/usr/bin/env python3
"""24 h fit for Peters gene contributions, or for a module score.

Contribution files have gene and contribution. The gene named score sets the
reference phase. Module files have module and value.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oscillation import rhythm_table

TWO_PI = 2.0 * np.pi


def _read(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "participant" not in frame.columns or "time" not in frame.columns:
        raise SystemExit(f"{path} needs participant and time columns")
    frame["time"] = pd.to_numeric(frame["time"], errors="coerce")
    return frame


def _contributions(frame: pd.DataFrame) -> pd.DataFrame:
    if "contribution" not in frame.columns or "gene" not in frame.columns:
        raise SystemExit("a contribution table needs gene and contribution columns")
    work = frame.rename(columns={"contribution": "value", "gene": "clock"})
    work["condition"] = "contribution"
    fitted = rhythm_table(work, ["clock"])
    reference = fitted.loc[fitted["clock"].astype(str) == "score", "acrophase_hour"]
    if len(reference):
        peak = float(reference.iloc[0])
        fitted["aligned_peak_to_trough"] = fitted["peak_to_trough"] * np.cos(
            TWO_PI * (fitted["acrophase_hour"] - peak) / 24.0
        )
    fitted = fitted.rename(columns={"clock": "gene"})
    rank = "aligned_peak_to_trough" if "aligned_peak_to_trough" in fitted.columns else "peak_to_trough"
    return fitted.sort_values(rank, ascending=False)


def _modules(frame: pd.DataFrame) -> pd.DataFrame:
    if "value" not in frame.columns:
        raise SystemExit("a module table needs a value column")
    work = frame.rename(columns={"module": "clock"})
    if "condition" not in work.columns:
        work["condition"] = "module"
    fitted = rhythm_table(work, ["clock"])
    return fitted.rename(columns={"clock": "module"})


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: python analysis/transcriptomic_drivers.py table.csv results.csv")
    frame = _read(sys.argv[1])
    if "gene" in frame.columns:
        result = _contributions(frame)
    elif "module" in frame.columns:
        result = _modules(frame)
    else:
        raise SystemExit("the table needs a gene column or a module column")
    result.to_csv(sys.argv[2], index=False)


if __name__ == "__main__":
    main()
