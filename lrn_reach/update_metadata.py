import re
import pandas as pd
from pathlib import Path

# --- EDIT THESE ---
INPUT_CSV = "video_list.csv"   # your CSV file
PATH_COLUMN = "file_path"           # the column in your CSV that holds full paths
OUTPUT_CSV = "video_metadata_parsed_it2.csv"
# ------------------

def parse_row(p):
    if pd.isna(p):
        return pd.Series({
            "file_path": None,
            "date": None,
            "timestamp": None,
            "camera_number": None,
            "rat_number": None,
            "movie_name": None
        })

    p_str = str(p).strip().strip('"').strip("'")
    path = Path(p_str)
    parts = list(path.parts)

    # camera_number from "cam#"
    camera_number = None
    for part in parts:
        m = re.match(r"(?i)^cam(\d+)$", part)
        if m:
            camera_number = m.group(1)
            break

    # rat_number from "rat###left/right" or "rat###"
    rat_number = None
    for part in parts:
        m = re.match(r"(?i)^rat(\d+)(?:left|right)?$", part)
        if m:
            rat_number = m.group(1)
            break

    # movie_name is the full filename
    movie_name = path.name if path.name else None

    date = None
    timestamp = None

    # First try from filename
    if movie_name:
        m = re.match(r"^(\d{4}-\d{2}-\d{2})_(\d{2})_(\d{2})_(\d{2})_", movie_name)
        if m:
            date = m.group(1)
            timestamp = f"{m.group(2)}:{m.group(3)}:{m.group(4)}"

    # If not found, try from folder name
    if date is None or timestamp is None:
        for part in reversed(parts[:-1]):  # skip filename
            m2 = re.match(r"^(\d{4}-\d{2}-\d{2})_(\d{2})_(\d{2})_(\d{2})_", part)
            if m2:
                date = m2.group(1)
                timestamp = f"{m2.group(2)}:{m2.group(3)}:{m2.group(4)}"
                break

    return pd.Series({
        "file_path": p_str,
        "date": date,
        "timestamp": timestamp,
        "camera_number": camera_number,
        "rat_number": rat_number,
        "movie_name": movie_name
    })

def main():
    df_in = pd.read_csv(INPUT_CSV)
    if PATH_COLUMN not in df_in.columns:
        raise ValueError(f"'{PATH_COLUMN}' not found in CSV. Columns: {list(df_in.columns)}")

    df_out = df_in[PATH_COLUMN].apply(parse_row)
    df_out.to_csv(OUTPUT_CSV, index=False)
    print(f"Wrote {len(df_out)} rows to {OUTPUT_CSV}")
    print(df_out.head())

if __name__ == "__main__":
    main()






import re
from pathlib import Path
import pandas as pd

# --- EDIT THIS ---
DLC_DIR = "/zfsr01/storage/gavin_lrn/LRN_reach-gtk-2025-07-08/complete/iteration01_flippedonly"
# -----------------

STEP_RE = re.compile(r"_(\d{4,})\.csv$", re.IGNORECASE)

def build_dlc_csv_index(dlc_dir: str) -> pd.DataFrame:
    """
    Walk DLC_DIR (recursively) and index DLC CSVs.
    Returns columns: ['dlc_prefix','csv_name','csv_path','dlc_step'].
    dlc_prefix is everything before 'DLC_' in the filename (preserves '_flipped' if present).
    """
    rows = []
    for p in Path(dlc_dir).rglob("*.csv"):
        name = p.name
        parts = name.split("DLC_", 1)
        if len(parts) != 2:
            continue  # skip non-DLC csvs
        dlc_prefix = parts[0]  # e.g., '2025-07-03_12_00_05_camcommerb1_wbgam_h264_flipped'
        m = STEP_RE.search(name)
        step = int(m.group(1)) if m else -1
        rows.append({
            "dlc_prefix": dlc_prefix,
            "csv_name": name,
            "csv_path": str(p.resolve()),
            "dlc_step": step
        })
    return pd.DataFrame(rows)

def add_dlc_columns(df: pd.DataFrame, dlc_dir: str) -> pd.DataFrame:
    """
    Adds DLC_data_output and DLC_data_path to df by matching:
      movie_prefix == dlc_prefix
    where movie_prefix = movie_name without the '.mp4' extension (keeps '_flipped' if present).
    If multiple CSVs match a prefix, keep the one with the largest training step.
    """
    dlc_df = build_dlc_csv_index(dlc_dir)
    df = df.copy()
    if dlc_df.empty:
        df["DLC_data_output"] = pd.NA
        df["DLC_data_path"] = pd.NA
        return df

    # keep best CSV per prefix (highest step)
    dlc_df = dlc_df.sort_values(["dlc_prefix", "dlc_step"], ascending=[True, False])
    dlc_best = dlc_df.drop_duplicates(subset=["dlc_prefix"], keep="first")

    # movie_prefix: strip only the .mp4 extension; DO NOT strip '_flipped'
    df["movie_prefix"] = df["movie_name"].astype(str).str.replace(r"\.mp4$", "", regex=True)

    # map prefixes to outputs/paths
    prefix_to_csv = dict(zip(dlc_best["dlc_prefix"], dlc_best["csv_name"]))
    prefix_to_path = dict(zip(dlc_best["dlc_prefix"], dlc_best["csv_path"]))

    df["DLC_data_output"] = df["movie_prefix"].map(prefix_to_csv)
    df["DLC_data_path"] = df["movie_prefix"].map(prefix_to_path)

    # optional: drop helper
    df.drop(columns=["movie_prefix"], inplace=True)
    return df

# ==== USAGE ====
df = add_dlc_columns(df, DLC_DIR)
# df.to_csv("video_metadata_with_dlc_links.csv", index=False)
