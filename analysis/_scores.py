"""CSV of clock predictions."""

from __future__ import annotations

import pandas as pd

REQUIRED = ["participant", "time", "condition", "clock", "value"]


def read_scores(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"{path} is missing columns: {', '.join(missing)}")
    df["time"] = pd.to_numeric(df["time"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df


def rhythm_groups(df):
    if "cohort" in df.columns:
        return ["cohort", "clock"], ["cohort"]
    return ["clock"], None
