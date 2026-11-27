"""Subject-centered 24 h cosinor and a within-subject time permutation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

TWO_PI = 2.0 * np.pi


def benjamini_hochberg(p_values) -> np.ndarray:
    p = np.asarray(p_values, dtype=float)
    q = np.full(p.shape, np.nan)
    ok = np.isfinite(p)
    if ok.any():
        _, adjusted, _, _ = multipletests(p[ok], method="fdr_bh")
        q[ok] = adjusted
    return q


def _groups(subject):
    return [np.flatnonzero(subject == s) for s in pd.unique(subject)]


def _center(y, groups):
    out = np.array(y, dtype=float, copy=True)
    for idx in groups:
        out[idx] -= np.mean(out[idx])
    return out


def _ols(t, y):
    # y is already subject-centered. Intercept absorbs what centering leaves.
    ang = TWO_PI * t / 24.0
    X = np.column_stack([np.ones(len(t)), np.cos(ang), np.sin(ang)])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    a, b = float(coef[1]), float(coef[2])
    amp = float(np.hypot(a, b))
    # peak of a*cos + b*sin
    peak = float((np.arctan2(b, a) % TWO_PI) * 24.0 / TWO_PI)
    return amp, peak


def fit_rhythm(df, value="value", participant="participant", time="time", n_perm=499, seed=1):
    d = df.dropna(subset=[value, participant, time])
    d = d[np.isfinite(d[value]) & np.isfinite(d[time])]
    subject = d[participant].to_numpy()
    t = d[time].to_numpy(dtype=float)
    y = d[value].to_numpy(dtype=float)
    out = {
        "n": int(len(d)),
        "n_participants": int(pd.unique(subject).size) if len(d) else 0,
        "peak_to_trough": np.nan,
        "acrophase_hour": np.nan,
        "p_perm": np.nan,
    }
    if out["n_participants"] < 2 or out["n"] < 4:
        return out

    groups = _groups(subject)
    yc = _center(y, groups)
    amp, peak = _ols(t, yc)
    out["peak_to_trough"] = 2.0 * amp
    out["acrophase_hour"] = peak

    rng = np.random.default_rng(seed)
    n_ge = 0
    for _i in range(n_perm):
        tp = t.copy()
        for idx in groups:
            tp[idx] = rng.permutation(tp[idx])
        if _ols(tp, yc)[0] >= amp:
            n_ge += 1
    out["p_perm"] = (n_ge + 1) / (n_perm + 1)
    return out


def rhythm_table(df, groups, family=None, n_perm=499, seed=1):
    rows = []
    for key, sub in df.groupby(groups, dropna=False):
        if not isinstance(key, tuple):
            key = (key,)
        row = dict(zip(groups, key))
        row.update(fit_rhythm(sub, n_perm=n_perm, seed=seed))
        rows.append(row)
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    if family:
        out["q_perm"] = out.groupby(family, dropna=False)["p_perm"].transform(benjamini_hochberg)
    else:
        out["q_perm"] = benjamini_hochberg(out["p_perm"].to_numpy())
    return out
