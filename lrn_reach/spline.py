import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
import yaml
import re


def load_spline_targets(config_path: str, df_cols: list[str]):
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f) or {}

    defaults  = cfg.get("defaults") or {}
    overrides = cfg.get("overrides") or {}
    explicit  = cfg.get("columns") or []
    patterns  = [re.compile(p) for p in (cfg.get("patterns") or [])]

    ordered, seen = [], set()
    for c in explicit:
        if c in df_cols and c not in seen:
            ordered.append(c); seen.add(c)
    for col in df_cols:
        if col in seen: 
            continue
        if any(p.search(col) for p in patterns):
            ordered.append(col); seen.add(col)

    per_col = {}
    for c in ordered:
        p = dict(defaults)
        p.update(overrides.get(c, {}))
        per_col[c] = p

    return ordered, per_col


def spline_filter_by_group(
    df: pd.DataFrame,
    config_path: str,
    group_col: str = "timestamp",
    order_col: str | None = None,  # if you have a frame index, put it here; else uses row order
) -> pd.DataFrame:
    """
    Apply UnivariateSpline per 'group_col' (e.g., timestamp) to selected columns from YAML.
    Each unique value of group_col is treated as a video block.
    """
    out = df.copy()
    targets, per_col_params = load_spline_targets(config_path, out.columns.tolist())
    if not targets:
        raise ValueError("No target columns selected by YAML config.")

    # Prepare output columns
    for c in targets:
        out[f"{c}_spline"] = np.nan

    # optional: remember original order if needed
    if order_col is None:
        out["_row_order___"] = np.arange(len(out))
        order_col_use = "_row_order___"
    else:
        order_col_use = order_col

    # Group by timestamp (47 unique values → 47 videos)
    for gval, gdf in out.groupby(group_col, sort=False):
        # sort within group to get frame order
        gidx = gdf.sort_values(order_col_use).index
        x = np.arange(len(gidx), dtype=float)

        for c in targets:
            params = per_col_params[c]
            k = int(params.get("k", 3))
            s = params.get("s", None)
            nan_strategy = str(params.get("nan_strategy", "interp"))

            y = pd.to_numeric(out.loc[gidx, c], errors="coerce").to_numpy(dtype=float)
            valid = np.isfinite(y)
            if not valid.any():
                continue

            src_x, src_y = x, y.copy()

            if nan_strategy == "interp":
                if valid.sum() >= 2:
                    src_y = (
                        pd.Series(y)
                        .interpolate("linear", limit_direction="both")
                        .to_numpy()
                    )
                else:
                    # single valid point → constant fallback
                    idx = int(np.flatnonzero(valid)[0])
                    src_y = np.full_like(y, y[idx])
            elif nan_strategy == "ffill":
                src_y = pd.Series(y).ffill().bfill().to_numpy()
            elif nan_strategy == "bfill":
                src_y = pd.Series(y).bfill().ffill().to_numpy()
            elif nan_strategy == "drop":
                src_x = x[valid]
                src_y = y[valid]

            # ensure enough unique x for requested k
            k_local = min(k, max(1, len(np.unique(src_x)) - 1))
            if len(src_x) <= k_local:
                k_local = 1  # linear fallback

            try:
                spl = UnivariateSpline(src_x, src_y, k=k_local, s=s)
                y_smooth = spl(x)
            except Exception:
                # robust fallback if fitting fails
                if nan_strategy == "drop":
                    tmp = pd.Series(np.nan, index=np.arange(len(x), dtype=int))
                    idxs = np.round(src_x).astype(int)
                    tmp.loc[idxs] = src_y
                    y_smooth = tmp.interpolate("linear", limit_direction="both").to_numpy()
                else:
                    y_smooth = src_y

            out.loc[gidx, f"{c}_spline"] = y_smooth

    if "_row_order___" in out.columns:
        out.drop(columns=["_row_order___"], inplace=True)

    return out

# ---------- Example ----------
df = pd.read_csv("final_mungmeta.csv")
smoothed = spline_filter_by_group(df, "spline_yam.yaml", group_col="timestamp", order_col=None)
smoothed.to_csv("smoothed.csv", index=False)
