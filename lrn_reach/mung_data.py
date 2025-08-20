from pathlib import Path
import re
import pandas as pd

DLC_HEADER_ROWS = [0, 1, 2]          # scorer / bodyparts / coords
DEFAULT_PATTERN = "*DLC_*.csv"       # adjust if your files use a different suffix

def _movie_stem_from_dlc(name: str) -> str:
    """Strip extension and everything from 'DLC' onward."""
    base = re.sub(r"\.(csv|CSV)$", "", name)
    base = re.sub(r"DLC.*$", "", base)  # drop DLC suffix and beyond
    return base

def _movie_stem_from_movie_name(movie_name: str) -> str:
    """Drop .mp4 from metadata movie_name."""
    return re.sub(r"\.mp4$", "", str(movie_name), flags=re.IGNORECASE)

def _read_dlc_csv(path: Path) -> pd.DataFrame:
    """Read DLC CSV (3-row header) and flatten columns to 'part_coord' + add 'frame'."""
    df = pd.read_csv(path, header=DLC_HEADER_ROWS)
    if not isinstance(df.columns, pd.MultiIndex) or df.columns.nlevels != 3:
        raise ValueError(f"{path.name} is not a 3-row header DLC CSV.")
    # drop level0 (scorer), keep (bodyparts, coords)
    df.columns = pd.MultiIndex.from_tuples([(b, c) for (_, b, c) in df.columns])
    df.columns = [f"{b}_{c}" for (b, c) in df.columns]  # e.g., scapula_x, scapula_y, scapula_likelihood
    df.insert(0, "frame", range(len(df)))
    return df

def merge_dlc_with_metadata(
    data_dir: str | Path,
    metadata_path: str | Path,
    output_path: str | Path,
    pattern: str = DEFAULT_PATTERN,
    excel: bool = False,
    sheet_name: str = "data",
    strict: bool = False,
    verbose: bool = True,
) -> pd.DataFrame:
    """
    Build a long-format dataset:
    - For each DLC CSV in data_dir, read per-frame rows, flatten columns, derive movie_stem.
    - Derive movie_stem from metadata.movie_name (drop .mp4).
    - Merge per-frame rows with the matching metadata row (broadcast metadata).
    - Set index to metadata.file_path (duplicates allowed). Add __dlc_source_* bookkeeping.
    - Save CSV or Excel. Returns the merged DataFrame.
    """
    data_dir = Path(data_dir)
    metadata_path = Path(metadata_path)
    output_path = Path(output_path)

    if not data_dir.is_dir():
        raise FileNotFoundError(f"--data-dir not found: {data_dir}")
    if not metadata_path.exists():
        raise FileNotFoundError(f"--metadata not found: {metadata_path}")

    # Load metadata (CSV or pickled DataFrame)
    if metadata_path.suffix.lower() == ".pkl":
        meta = pd.read_pickle(metadata_path)
    else:
        meta = pd.read_csv(metadata_path)

    meta.columns = [str(c).strip() for c in meta.columns]
    if "movie_name" not in meta.columns:
        raise KeyError("Metadata must include 'movie_name' column.")
    meta["movie_stem"] = meta["movie_name"].map(_movie_stem_from_movie_name)

    dlc_files = sorted(data_dir.glob(pattern))
    if verbose:
        print(f"[INFO] Found {len(dlc_files)} DLC CSVs in {data_dir} matching '{pattern}'")

    parts: list[pd.DataFrame] = []
    for p in dlc_files:
        try:
            dlc = _read_dlc_csv(p)
        except Exception as e:
            msg = f"[ERROR] {p.name}: {e}"
            if strict:
                raise RuntimeError(msg)
            if verbose:
                print(msg)
            continue

        stem = _movie_stem_from_dlc(p.stem)
        m = meta.loc[meta["movie_stem"] == stem]
        if m.empty:
            msg = f"[WARN] No metadata match for {p.name} (movie_stem={stem})"
            if strict:
                raise RuntimeError(msg)
            if verbose:
                print(msg)
            continue
        if len(m) > 1 and verbose:
            print(f"[INFO] Multiple metadata rows matched for {p.name}; using the first.")

        meta_row = m.iloc[[0]].copy()
        meta_repeated = pd.concat([meta_row] * len(dlc), ignore_index=True)
        meta_repeated.index = range(len(dlc))

        out = pd.concat([dlc, meta_repeated], axis=1)
        if "file_path" in out.columns:
            out = out.set_index("file_path", drop=True)
        else:
            # fallback: index by movie_stem
            out = out.set_index(pd.Index([stem] * len(out), name="file_path"))

        out["__dlc_source_file"] = p.name
        out["__dlc_source_path"] = str(p)
        parts.append(out)

        if verbose:
            print(f"[OK] {p.name}: {len(dlc)} frames merged")

    if not parts:
        raise RuntimeError("No DLC files were merged. Check your pattern and metadata matches.")

    merged = pd.concat(parts, axis=0, ignore_index=False)

    # Order columns: frame + DLC coords first, then metadata, then bookkeeping
    first_cols = [c for c in merged.columns if (c == "frame") or re.match(r".*_(x|y|likelihood)$", str(c) or "")]
    book_cols = [c for c in ["__dlc_source_file", "__dlc_source_path"] if c in merged.columns]
    meta_cols = [c for c in merged.columns if c not in first_cols + book_cols]

    merged = merged[first_cols + meta_cols + book_cols]

    # Save
    if excel:
        outp = output_path.with_suffix(".xlsx") if output_path.suffix.lower() != ".xlsx" else output_path
        with pd.ExcelWriter(outp, engine="openpyxl") as xw:
            merged.to_excel(xw, sheet_name=sheet_name)
        if verbose:
            print(f"[DONE] Wrote Excel → {outp}")
    else:
        outp = output_path.with_suffix(".csv") if output_path.suffix.lower() != ".csv" else output_path
        merged.to_csv(outp)
        if verbose:
            print(f"[DONE] Wrote CSV → {outp}")

    return merged
