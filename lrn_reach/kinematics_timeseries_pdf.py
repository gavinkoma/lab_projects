import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np

BODYPARTS = ["scapula", "shoulder", "elbow", "wrist", "MCP"]

def plot_reach_timeseries(df: pd.DataFrame, out_pdf: str):
    """
    For each movie_stem:
      - Left: plot x & y over all 1000 frames, with reach_start/end marked
      - Right: plot x & y only from reach_start to reach_end
    Saves a multi-page PDF.
    """
    with PdfPages(out_pdf) as pdf:
        for movie_stem, g in df.groupby("movie_stem", sort=False):
            g = g.reset_index(drop=True)

            frames = g["frame"].to_numpy()

            # reach start/end (same across all rows in group)
            r_start = int(g["reach_start"].iloc[0]) if pd.notnull(g["reach_start"].iloc[0]) else None
            r_end   = int(g["reach_end"].iloc[0])   if pd.notnull(g["reach_end"].iloc[0])   else None

            fig, (ax_full, ax_reach) = plt.subplots(
                1, 2, figsize=(11, 8.5), gridspec_kw={"width_ratios":[2,1]}
            )

            # --- Left: full series ---
            for bp in BODYPARTS:
                for ax_name, linestyle in zip(["x","y"], ["-","--"]):
                    col = f"{bp}_{ax_name}"
                    if col in g.columns:
                        ax_full.plot(frames, g[col], linestyle=linestyle, label=col)

            # add vertical lines for reach start/end
            if r_start is not None:
                ax_full.axvline(r_start, color="green", linestyle="--", linewidth=1.2, label="reach_start")
            if r_end is not None:
                ax_full.axvline(r_end, color="red", linestyle="--", linewidth=1.2, label="reach_end")

            ax_full.set_title(f"{movie_stem} — Full (0–999)")
            ax_full.set_xlabel("Frame")
            ax_full.set_ylabel("Pixels")
            ax_full.legend(fontsize=6)

            # --- Right: reach slice ---
            if r_start is not None and r_end is not None and r_end > r_start:
                mask = (frames >= r_start) & (frames <= r_end)
                for bp in BODYPARTS:
                    for ax_name, linestyle in zip(["x","y"], ["-","--"]):
                        col = f"{bp}_{ax_name}"
                        if col in g.columns:
                            ax_reach.plot(frames[mask], g.loc[mask, col],
                                          linestyle=linestyle, label=col)
                ax_reach.set_title(f"Reach ({r_start}–{r_end})")
                ax_reach.set_xlabel("Frame")
                ax_reach.set_ylabel("Pixels")
            else:
                ax_reach.text(0.5, 0.5, "No valid reach",
                              ha="center", va="center", transform=ax_reach.transAxes)
                ax_reach.axis("off")

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    print(f"Saved PDF to {out_pdf}")

plot_reach_timeseries(df, "kinematics_timeseries.pdf")

