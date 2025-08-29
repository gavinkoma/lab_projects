import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # safe in headless envs
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def find_spline_pairs(df):
    """
    Find all (base_col, spline_col) pairs in a dataframe.
    Example: ('hip_x', 'hip_x_spline').
    """
    pairs = []
    for col in df.columns:
        if col.endswith("_spline"):
            base = col[:-7]
            if base in df.columns:
                pairs.append((base, col))
    return pairs

def qc_pdf(df, pairs=None, out_pdf="qc_spline_overlays.pdf",
           group_col="timestamp", order_col="frame"):
    """
    Create a multi-page PDF with original vs spline plots.

    Parameters
    ----------
    df : DataFrame
        Must contain original columns and *_spline columns.
    pairs : list of tuples, optional
        List of (base, spline) columns. If None, auto-detect.
    out_pdf : str
        Path for output PDF.
    group_col : str
        Column to group by (usually 'timestamp').
    order_col : str
        Column to sort within groups (usually 'frame').
    """
    if pairs is None:
        pairs = find_spline_pairs(df)

    pages = 0
    with PdfPages(out_pdf) as pdf:
        for gval, gdf in df.groupby(group_col, sort=False):
            if order_col in gdf.columns:
                gdf = gdf.sort_values(order_col)
            x = np.arange(len(gdf))
            for base, spl in pairs:
                y_orig = pd.to_numeric(gdf[base], errors="coerce").to_numpy()
                y_spl  = pd.to_numeric(gdf[spl], errors="coerce").to_numpy()
                if not (np.any(np.isfinite(y_orig)) or np.any(np.isfinite(y_spl))):
                    continue
                plt.figure(figsize=(9,4))
                plt.plot(x, y_orig, lw=1.0, label=f"{base} (orig)")
                plt.plot(x, y_spl,  lw=1.5, label=f"{spl}")
                plt.title(f"{base} — {group_col} {gval}")
                plt.xlabel("frame index")
                plt.ylabel(base)
                plt.legend()
                plt.tight_layout()
                pdf.savefig(); plt.close()
                pages += 1

        if pages == 0:
            plt.figure()
            plt.text(0.5,0.5,"No plots generated", ha="center", va="center")
            pdf.savefig(); plt.close()

    print(f"[OK] wrote {out_pdf}")
    return out_pdf



df = df2
qc_pdf(df, out_pdf="qc_spline_overlays.pdf")
