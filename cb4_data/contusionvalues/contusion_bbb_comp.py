import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# ---------- Paths ----------
PATH_CONTUSION = "/Users/gavinkoma/Documents/lab_projects/cb4_data/contusionvalues/infinite_horizon_kdyn.csv.xlsx"
PATH_BBB       = "/Users/gavinkoma/Documents/lab_projects/cb4_data/cb2cb3cb4_BBBdata.xlsx"

# ---------- Constants ----------
ALLOWED_RATS = {
    142,143,144,147,179,215,216,217,218,224,
    405,406,414,504,521,523,524,525,528
}
EXP_COLOR = "#1f77b4"
CTRL_COLOR = "#ff7f0e"
EXP_MARK  = "s"
CTRL_MARK = "o"

# ---------- Helpers ----------
def ttest_label(a, b):
    a = pd.Series(a).dropna().astype(float)
    b = pd.Series(b).dropna().astype(float)
    if len(a) < 2 or len(b) < 2: return "n<2"
    stat, p = ttest_ind(a, b, equal_var=False)
    stars = "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "n.s."
    return f"p={p:.3g} {stars}"

def normalize_week(x):
    if pd.isna(x): return np.nan
    s = str(x).strip().lower().replace("_", " ")
    s = re.sub(r"\s+", " ", s)
    if "base" in s: return "baseline"
    if "wk1" in s or "week 1" in s or "week1" in s: return "week1"
    return s

def nice_box(ax, data_dict, x_positions, box_width=0.35, color_map=None, marker_map=None):
    if color_map is None: color_map = {}
    if marker_map is None: marker_map = {}
    for i, (label, vals) in enumerate(data_dict.items()):
        pos = x_positions[i]
        y = pd.Series(vals).dropna().astype(float).values
        bp = ax.boxplot([y], positions=[pos], widths=box_width,
                        patch_artist=True, showfliers=False)
        face = color_map.get(label)
        for patch in bp['boxes']:
            if face: patch.set(facecolor=face, alpha=0.35)
        for median in bp['medians']:
            median.set(linewidth=2)
        if y.size:
            jitter = (np.random.rand(y.size) - 0.5) * (box_width * 0.6)
            ax.scatter(np.full_like(y, pos, dtype=float) + jitter, y,
                       s=24, alpha=0.8, c=(face if face else None),
                       marker=marker_map.get(label, "o"))

def col(df, name):
    for c in df.columns:
        if str(c).strip().lower() == name:
            return c
    raise KeyError(f"Column '{name}' not found in {list(df.columns)}")

# ---------- LEFT PLOT DATA: contusion ----------
contusion_raw = pd.read_excel(PATH_CONTUSION)

c_rat   = col(contusion_raw, "rat_num")
c_group = col(contusion_raw, "group")
c_value = col(contusion_raw, "actual_value")

contusion_df = contusion_raw[[c_rat, c_group, c_value]].rename(
    columns={c_rat:"rat_num", c_group:"group", c_value:"value"}
)
contusion_df["group"] = (
    contusion_df["group"].astype(str).str.strip().str.lower()
    .str.replace(r"\s+", " ", regex=True)
    .replace({"experimental":"experimental", "exp":"experimental",
              "control":"control", "ctrl":"control"})
)
# filter to allowed rats
contusion_df = contusion_df[contusion_df["rat_num"].astype(int).isin(ALLOWED_RATS)]

exp_vals  = contusion_df.loc[contusion_df["group"]=="experimental", "value"].astype(float).dropna().values
ctrl_vals = contusion_df.loc[contusion_df["group"]=="control",      "value"].astype(float).dropna().values

# ---------- RIGHT PLOT DATA: BBB (build bbb_long) ----------
bbb = pd.read_excel(PATH_BBB)

# Left half columns (week, rat, type, BBB score)
left_map = {}
for need in ["week","rat","bbb score","type"]:
    match = [c for c in bbb.columns if str(c).strip().lower() == need]
    if match: left_map[need] = match[0]
left_df = bbb[[left_map["week"], left_map["rat"], left_map["type"], left_map["bbb score"]]].copy()
left_df.columns = ["week","rat","type","score"]

# Right half: many 'Unnamed' columns pack (week, rat, type, score) again
right_df = pd.DataFrame(columns=["week","rat","type","score"])
cols = list(bbb.columns)
for i in range(len(cols)-3):
    block = cols[i:i+4]
    if not any("Unnamed" in str(x) for x in block): 
        continue
    tmp = bbb[block].copy()
    tmp.columns = ["c0","c1","c2","c3"]

    def weeklike(s): return s.astype(str).str.contains("base|week", case=False, na=False).mean() > 0.2
    def typelike(s):  return s.astype(str).str.contains("exp|ctrl|control|experimental", case=False, na=False).mean() > 0.2

    candidates = {}
    for name in ["c0","c1","c2","c3"]:
        s = tmp[name]
        if weeklike(s): candidates['week'] = name
        if typelike(s): candidates['type'] = name

    remaining = [n for n in ["c0","c1","c2","c3"] if n not in candidates.values()]
    rat_name = score_name = None
    for n in remaining:
        s = pd.to_numeric(tmp[n], errors="coerce")
        if s.notna().mean() > 0.6:
            med = s.median()
            if 0 <= med <= 30 and score_name is None: score_name = n
            elif med > 30 and rat_name is None: rat_name = n

    if {'week','type'} <= set(candidates) and rat_name and score_name:
        sub = tmp[[candidates['week'], rat_name, candidates['type'], score_name]].copy()
        sub.columns = ["week","rat","type","score"]
        right_df = pd.concat([right_df, sub], ignore_index=True)

bbb_long = pd.concat([left_df, right_df], ignore_index=True)

# clean/normalize
bbb_long["week"] = bbb_long["week"].apply(normalize_week)
bbb_long["type"] = (
    bbb_long["type"].astype(str).str.strip().str.lower()
    .replace({"experimental":"exp","control":"ctrl"})
)
bbb_long["rat"]   = pd.to_numeric(bbb_long["rat"], errors="coerce")
bbb_long["score"] = pd.to_numeric(bbb_long["score"], errors="coerce")

# filter to baseline/week1 + allowed rats + valid types
bbb_long = bbb_long[
    bbb_long["week"].isin(["baseline","week1"]) &
    bbb_long["type"].isin(["exp","ctrl"]) &
    bbb_long["rat"].isin(ALLOWED_RATS)
].copy()

# ---------- PLOTTING ----------
plt.figure(figsize=(12, 5))

# (1,1) LEFT: contusion by group
ax1 = plt.subplot(1, 2, 1)
vals_left = {"Experimental": exp_vals, "Control": ctrl_vals}
xpos_left = [0, 1]
nice_box(ax1, vals_left, xpos_left, box_width=0.28,
         color_map={"Experimental": EXP_COLOR, "Control": CTRL_COLOR},
         marker_map={"Experimental": EXP_MARK,  "Control": CTRL_MARK})
ax1.set_xticks(xpos_left)
ax1.set_xticklabels(["Experimental", "Control"])
ax1.set_ylabel("Actual Value (kDyn)")
ax1.set_title("Contusion Values by Group")

lab = ttest_label(exp_vals, ctrl_vals)
if exp_vals.size or ctrl_vals.size:
    ymax = np.nanmax(np.concatenate([exp_vals, ctrl_vals]))
    ax1.set_ylim(top=ymax * 1.008)  # add some headroom
    ax1.annotate(
        lab,
        xy=(0.5, ymax),
        xytext=(0, 10), textcoords="offset points",
        ha="center", va="bottom", fontsize=10,
        annotation_clip=False,
        bbox=dict(facecolor="white", alpha=0.7, boxstyle="round,pad=0.2")  # optional background
    )

# (2,1) RIGHT: BBB baseline vs week1, split by type with consistent style
ax2 = plt.subplot(1, 2, 2)
weeks = ["baseline", "week1"]
centers = [0, 1]; delta = 0.14; box_w = 0.22

for i, wk in enumerate(weeks):
    exp_wk  = bbb_long[(bbb_long["week"]==wk) & (bbb_long["type"]=="exp")]["score"].values
    ctrl_wk = bbb_long[(bbb_long["week"]==wk) & (bbb_long["type"]=="ctrl")]["score"].values
    vals = {"exp": exp_wk, "ctrl": ctrl_wk}
    nice_box(ax2, vals, [centers[i]-delta, centers[i]+delta], box_width=box_w,
             color_map={"exp": EXP_COLOR, "ctrl": CTRL_COLOR},
             marker_map={"exp": EXP_MARK, "ctrl": CTRL_MARK})
    if len(exp_wk) + len(ctrl_wk):
        pair_max = np.nanmax(np.concatenate([pd.Series(v).dropna().values for v in vals.values()]))
        ax2.margins(y=0.15)  # add some headroom globally
        ax2.annotate(
            ttest_label(exp_wk, ctrl_wk),
            xy=(centers[i], pair_max),
            xytext=(0, 10), textcoords="offset points",
            ha="center", va="bottom", fontsize=10,
            annotation_clip=False,
            bbox=dict(facecolor="white", alpha=0.7, boxstyle="round,pad=0.2")
        )


ax2.set_xticks(centers)
ax2.set_xticklabels(["Baseline", "Week 1"])
ax2.set_ylabel("BBB Score")
ax2.set_title("BBB Scores by Week and Group")

handles = [
    plt.Line2D([], [], linestyle="none", marker=EXP_MARK, markersize=8, color=EXP_COLOR, label="exp"),
    plt.Line2D([], [], linestyle="none", marker=CTRL_MARK, markersize=8, color=CTRL_COLOR, label="ctrl"),
]
ax2.legend(handles=handles, frameon=False, loc="lower left", title="Group")

plt.tight_layout()
plt.show()
