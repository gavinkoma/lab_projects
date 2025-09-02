import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.interpolate import UnivariateSpline

# ------------ Tunables ------------
BODYPARTS = ["scapula", "shoulder", "elbow", "wrist", "MCP"]  # add/remove as needed
LIKELIHOOD_THRESH = 0.90
HAMPEL_WIN = 11          # odd number; frames
HAMPEL_K = 4.0           # how strict spike rejection is (MAD multiples) on velocity
MAX_SPEED_PX = None      # e.g., 40 to hard-cap velocity outliers; None to disable
SPLINE_S_FACTOR = 0.5    # smoothing strength ~ alpha * n_good_points
LINEWIDTH_RAW = 1.0
LINEWIDTH_SPL = 2.2
PDF_PATH = "splines_overlay.pdf"
# ----------------------------------

def _hampel_mask_velocity(y: np.ndarray, window: int, k: float) -> np.ndarray:
    """
    Returns boolean mask of 'good' samples based on a Hampel filter
    applied to velocity (first differences). True = keep, False = outlier.
    """
    v = np.diff(y, prepend=y[0])  # simple first difference
    # rolling median & MAD
    half = window // 2
    med = np.copy(v)
    mad = np.copy(v)
    for i in range(len(v)):
        lo = max(0, i - half)
        hi = min(len(v), i + half + 1)
        x = v[lo:hi]
        m = np.median(x)
        med[i] = m
        mad[i] = np.median(np.abs(x - m)) + 1e-9  # avoid zero
    z = np.abs(v - med) / (1.4826 * mad)
    mask = z <= k
    return mask

def _hardcap_velocity(y: np.ndarray, max_speed: float | None) -> np.ndarray:
    """
    Optional: flag points where instantaneous speed exceeds max_speed.
    """
    if max_speed is None:
        return np.ones_like(y, dtype=bool)
    v = np.abs(np.diff(y, prepend=y[0]))
    return v <= max_speed

def _fit_spline(frames: np.ndarray, y: np.ndarray, w: np.ndarray, good_mask: np.ndarray):
    # fit only on good points; fall back to simple interpolation if too few points
    xg = frames[good_mask]
    yg = y[good_mask]
    wg = w[good_mask]
    if len(xg) < 8:  # too few to spline — do linear interp
        y_fit = np.interp(frames, xg, yg) if len(xg) >= 2 else np.full_like(frames, np.nan, dtype=float)
        return y_fit
    s = SPLINE_S_FACTOR * len(xg)  # smoothing parameter scales with n
    try:
        spl = UnivariateSpline(xg, yg, w=wg, s=s, k=3)
        return spl(frames)
    except Exception:
        # If spline fails (e.g., not strictly increasing x), fall back to interp
        return np.interp(frames, xg, yg)

def _make_series_masks(df_vid: pd.DataFrame, coord_col: str, like_col: str | None):
    y = df_vid[coord_col].to_numpy(dtype=float)
    frames = df_vid["frame"].to_numpy(dtype=float)

    # Likelihood mask
    if like_col is not None and like_col in df_vid:
        like = df_vid[like_col].to_numpy(dtype=float)
        m_like = like >= LIKELIHOOD_THRESH
        w = np.clip((like - LIKELIHOOD_THRESH) / (1 - LIKELIHOOD_THRESH + 1e-9), 0, 1)
    else:
        m_like = np.ones_like(y, dtype=bool)
        w = np.ones_like(y, dtype=float)

    # Velocity-based masks
    m_hamp = _hampel_mask_velocity(y, HAMPEL_WIN, HAMPEL_K)
    m_cap = _hardcap_velocity(y, MAX_SPEED_PX)

    good = m_like & m_hamp & m_cap & np.isfinite(y)
    return frames, y, w, good

def _plot_one_movie(df_vid: pd.DataFrame, ax_full, ax_zoom, title: str):
    frames = df_vid["frame"].to_numpy(dtype=int)
    r0 = int(df_vid["reach_start"].iloc[0]) if "reach_start" in df_vid else None
    r1 = int(df_vid["reach_end"].iloc[0]) if "reach_end" in df_vid else None

    # (bp, axis, coord, like)
    to_plot = []
    for bp in BODYPARTS:
        for axis in ("x", "y"):
            coord = f"{bp}_{axis}"
            like = f"{bp}_likelihood"
            if coord in df_vid.columns:
                to_plot.append((bp, axis, coord, like if like in df_vid.columns else None))

    for bp, axis, coord, like in to_plot:
        f, y, w, good = _series_setup(df_vid, coord, like)
        y_fit = _fit_spline(f, y, w, good)

        # raw dashed
        ax_full.plot(f, y, "--", linewidth=LINEWIDTH_RAW, alpha=0.9, label=f"{bp}_{axis}")
        ax_zoom.plot(f, y, "--", linewidth=LINEWIDTH_RAW, alpha=0.9)

        # spline solid
        ax_full.plot(f, y_fit, linewidth=LINEWIDTH_SPL, alpha=0.95)
        ax_zoom.plot(f, y_fit, linewidth=LINEWIDTH_SPL, alpha=0.95)

    for ax in (ax_full, ax_zoom):
        ax.set_xlabel("Frame")
        ax.set_ylabel("Pixels")
        ax.set_ylim(0, 1600)  # <-- new fixed y-limitsss

        if r0 is not None:
            ax.axvline(r0, linestyle="--", color="green", linewidth=1.5)
        if r1 is not None:
            ax.axvline(r1, linestyle="--", color="red", linewidth=1.5)

    if r0 is not None and r1 is not None:
        pad = max(5, int(0.05 * max(1, r1 - r0)))
        ax_zoom.set_xlim(r0 - pad, r1 + pad)

    ax_full.set_title(f"{title} — Full (0–{frames.max():d})")
    ax_zoom.set_title(f"Reach ({r0}–{r1})" if r0 is not None and r1 is not None else "Reach (unavailable)")
    ax_full.legend(loc="upper right", fontsize=8, ncol=1, frameon=False)


def plot_filtered_splines(dfd: pd.DataFrame, pdf_path: str = PDF_PATH, skip_if_excluded=True):
    """
    For each movie_name group: plot raw vs spline-filtered traces for BODYPARTS.
    Produces a multi-page PDF.
    """
    assert "movie_name" in dfd.columns, "Expected 'movie_name' column."
    required = {"frame", "reach_start", "reach_end"}
    missing = [c for c in required if c not in dfd.columns]
    if missing:
        print("Warning: missing columns:", missing)

    with PdfPages(pdf_path) as pdf:
        for movie, df_vid in dfd.groupby("movie_name", sort=False):
            df_vid = df_vid.sort_values("frame").reset_index(drop=True)

            if skip_if_excluded and "exclude" in df_vid and str(df_vid["exclude"].iloc[0]).lower() in {"yes", "true", "1"}:
                continue

            # figure per movie
            fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(12, 8), constrained_layout=True)
            title = df_vid["movie_stem"].iloc[0] if "movie_stem" in df_vid else movie.replace(".mp4", "")
            _plot_one_movie(df_vid, ax_full, ax_zoom, title)
            pdf.savefig(fig, dpi=200)
            plt.close(fig)

    print(f"Wrote: {pdf_path}")
    return pdf_path


plot_filtered_splines(dfd)
