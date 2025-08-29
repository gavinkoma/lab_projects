import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator
from scipy.signal import savgol_filter

def _mad(x):
    x = np.asarray(x, float)
    m = np.nanmedian(x)
    return np.nanmedian(np.abs(x - m)) + 1e-12

def _hampel_flags(y, window=11, n_sigmas=3.5):
    s = pd.Series(y)
    med = s.rolling(window, center=True, min_periods=1).median()
    abs_dev = (s - med).abs()
    mad = abs_dev.rolling(window, center=True, min_periods=1).median()
    thr = n_sigmas * 1.4826 * mad.replace(0, np.nan)
    return (abs_dev > thr).to_numpy()

def _dilate(mask, pad=2):
    if pad <= 0: return mask
    k = np.ones(2*pad + 1, dtype=int)
    return np.convolve(mask.astype(int), k, mode="same") > 0

def _runs(mask):
    """Yield (i, j) inclusive indices for contiguous True runs."""
    i, n = 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j+1]:
                j += 1
            yield i, j
            i = j + 1
        else:
            i += 1

def repair_blips_strict_v3(
    df: pd.DataFrame,
    base_cols: list[str],
    group_col: str = "timestamp",
    order_col: str = "frame",
    like_abs_tau: float = 0.90,   # absolute low-likelihood floor
    like_rel_k: float = 2.5,      # relative floor: med - k*MAD
    anchor_tau: float = 0.98,     # frames >= this likelihood are never masked
    hampel_win: int = 11,
    pos_sig: float = 3.8,
    vel_sig: float = 5.0,
    pad: int = 2,
    short_gap: int = 6,           # <= short_gap → quadratic poly
    max_gap: int = 80,            # > max_gap → linear bridge
    edge_blend: int = 4,          # cosine taper width at each edge
    savgol_win: int = 7,          # must be odd; 0/None disables
    savgol_poly: int = 2,
    write_suffix: str = "_spline" # overwrite your *_spline
) -> pd.DataFrame:
    """
    Repairs DLC 'blips' without touching good frames.
    Inside each masked run:
      - length <= short_gap:  local quadratic (Savitzky–Golay style) across neighbors
      - short_gap < length <= max_gap: PCHIP across neighbors (shape-preserving)
      - length > max_gap: linear bridge
    Edges are cosine-blended to avoid kinks. Optional Savitzky–Golay smoothing
    is applied **inside the run only**.
    """
    out = df.copy()

    def like_col_for(base):
        joint = base.rsplit("_", 1)[0]
        c = f"{joint}_likelihood"
        return c if c in out.columns else None

    for ts, g in out.groupby(group_col, sort=False):
        g = g.sort_values(order_col)
        idx = g.index
        n   = len(idx)
        x   = np.arange(n, dtype=float)

        for base in base_cols:
            y = pd.to_numeric(g[base], errors="coerce").to_numpy(dtype=float)

            lcol = like_col_for(base)
            lk = pd.to_numeric(g[lcol], errors="coerce").to_numpy(dtype=float) if lcol else np.ones_like(y)

            # Likelihood-based mask: absolute + relative
            lk_med, lk_mad = np.nanmedian(lk), _mad(lk)
            rel_thr = lk_med - like_rel_k * 1.4826 * lk_mad
            like_bad = (lk < max(like_abs_tau, rel_thr))

            # Robust outliers (position + velocity)
            pos_out = _hampel_flags(y, window=hampel_win, n_sigmas=pos_sig)
            vel = np.diff(y, prepend=y[0])
            vel_out = _hampel_flags(vel, window=hampel_win, n_sigmas=vel_sig)

            # Only mark outliers as bad if not high-confidence
            not_anchor = lk < anchor_tau
            bad = (like_bad | ((pos_out | vel_out) & not_anchor) | ~np.isfinite(y))
            # expand around spikes, but protect anchors
            bad = _dilate(bad, pad=pad)
            bad[lk >= anchor_tau] = False

            y_out = y.copy()
            good = ~bad & np.isfinite(y)

            if good.sum() >= 2:
                gx, gy = x[good], y[good]
                # Precompute global interpolants we may use inside runs
                pchip = PchipInterpolator(gx, gy, extrapolate=True)
                y_pchip = pchip(x)
                y_lin   = np.interp(x, gx, gy)

                for i, j in _runs(bad):
                    L = j - i + 1
                    # Choose fill method by run length
                    if L <= short_gap:
                        # local quadratic using neighbors: take a window around [i..j]
                        left = max(0, i - max(4, short_gap))
                        right = min(n, j + 1 + max(4, short_gap))
                        seg = y_out[left:right].copy()
                        # build mask for unmasked points inside the segment
                        seg_good = np.isfinite(seg)
                        # simple poly fit on neighbors (fallback to linear if too few)
                        if seg_good.sum() >= 3:
                            # Fit small poly to neighbor points only
                            xs = np.arange(left, right, dtype=float)
                            ms = seg_good & ~((xs >= i) & (xs <= j))
                            if ms.sum() >= 3:
                                coeffs = np.polyfit(xs[ms] - xs[ms].mean(), seg[ms], deg=2)
                                fit = np.polyval(coeffs, xs - xs[ms].mean())
                                y_fill = fit
                            else:
                                y_fill = np.interp(xs, xs[seg_good], seg[seg_good])
                        else:
                            xs = np.arange(left, right, dtype=float)
                            y_fill = np.interp(xs, xs[seg_good], seg[seg_good])
                        # write back only the run
                        y_out[i:j+1] = y_fill[(i-left):(j-left+1)]
                    elif L <= max_gap:
                        y_out[i:j+1] = y_pchip[i:j+1]
                    else:
                        y_out[i:j+1] = y_lin[i:j+1]

                    # Optional inside-run Savitzky–Golay + edge taper
                    if savgol_win and L >= 5:
                        win = min(savgol_win, L if L % 2 == 1 else L-1)
                        if win >= 5:
                            seg = y_out[i:j+1].copy()
                            seg_s = savgol_filter(seg, window_length=win, polyorder=min(savgol_poly, win-1))
                            # cosine blend at edges to avoid kinks
                            r = min(edge_blend, L//2)
                            if r > 0:
                                t = (1 - np.cos(np.linspace(0, np.pi, 2*r))) / 2.0  # 0..1..0
                                w = np.ones(L)
                                w[:r]  = t[:r]
                                w[-r:] = t[-r:]
                                seg = (1-w)*seg + w*seg_s
                                seg_s = seg
                            y_out[i:j+1] = seg_s

            # write only repaired values at bad indices; good frames remain original
            out.loc[idx, f"{base}{write_suffix}"] = y_out

    return out

cols = ["scapula_x","scapula_y","shoulder_x","shoulder_y",
        "elbow_x","elbow_y","wrist_x","wrist_y","MCP_x","MCP_y"]

fdf = repair_blips_strict_v3(
    df, cols,
    group_col="timestamp", order_col="frame",
    like_abs_tau=0.90, like_rel_k=2.5, anchor_tau=0.98,
    hampel_win=11, pos_sig=3.8, vel_sig=5.0,
    pad=2, short_gap=6, max_gap=80, edge_blend=4,
    savgol_win=7, savgol_poly=2,
    write_suffix="_spline"
)








