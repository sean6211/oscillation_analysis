"""Matched-hour intervention contrast and a two-hour contrast.

Replicates at one hour are averaged. Hours missing from either arm are dropped.
Each remaining hour counts once, then the hours are averaged within participant.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from oscillation.cosinor import benjamini_hochberg


def _hour(time: pd.Series) -> pd.Series:
    return pd.to_numeric(time, errors="coerce").round(2)


def _one_sample(differences: list[float]) -> dict:
    values = np.asarray(differences, dtype=float)
    values = values[np.isfinite(values)]
    result = {"n_participants": int(len(values)), "mean_difference": np.nan, "p": np.nan}
    if len(values) >= 2:
        _statistic, p_value = stats.ttest_1samp(values, popmean=0.0)
        result["mean_difference"] = float(np.mean(values))
        result["p"] = float(p_value)
    return result


def _with_fdr(rows: list[dict]) -> pd.DataFrame:
    out = pd.DataFrame(rows)
    if not out.empty:
        out["q"] = benjamini_hochberg(out["p"].to_numpy())
    return out


def matched_hour_contrast(frame: pd.DataFrame, intervention: str, control: str) -> pd.DataFrame:
    """Intervention minus control at matched hours, corrected across clocks."""
    rows = []
    for clock, clocks in frame.groupby("clock", dropna=False):
        people = []
        work = clocks.copy()
        work["hour"] = _hour(work["time"])
        for _person, person_rows in work.groupby("participant"):
            hour_differences = []
            for _hour_value, hour_rows in person_rows.groupby("hour"):
                treated = hour_rows.loc[hour_rows["condition"] == intervention, "value"]
                untreated = hour_rows.loc[hour_rows["condition"] == control, "value"]
                if len(treated) and len(untreated):
                    hour_differences.append(float(treated.mean() - untreated.mean()))
            if hour_differences:
                people.append(float(np.mean(hour_differences)))
        row = {"clock": clock, "contrast": f"{intervention} - {control}"}
        row.update(_one_sample(people))
        rows.append(row)
    return _with_fdr(rows)


def time_of_day_contrast(
    frame: pd.DataFrame,
    later: float,
    earlier: float,
    control: str | None = None,
) -> pd.DataFrame:
    """Later hour minus earlier hour within one condition, corrected across clocks."""
    use = frame if control is None else frame[frame["condition"] == control]
    use = use.copy()
    use["hour"] = _hour(use["time"])
    later_hour = round(float(later), 2)
    earlier_hour = round(float(earlier), 2)
    rows = []
    for clock, clocks in use.groupby("clock", dropna=False):
        differences = []
        means = clocks.groupby(["participant", "hour"], as_index=False)["value"].mean()
        for _person, person_rows in means.groupby("participant"):
            after = person_rows.loc[person_rows["hour"] == later_hour, "value"]
            before = person_rows.loc[person_rows["hour"] == earlier_hour, "value"]
            if len(after) and len(before):
                differences.append(float(after.mean() - before.mean()))
        row = {"clock": clock, "contrast": f"{later_hour:g} - {earlier_hour:g}"}
        row.update(_one_sample(differences))
        rows.append(row)
    return _with_fdr(rows)
