#!/bin/bash
set -euo pipefail

# =====================
# Project paths
# =====================
PROJ=/wynton/scratch/aleberre/projects/Ginkgo_pipeline
SIF=/wynton/scratch/aleberre/containers/ginkgobv.sif

# dataset root (can override at runtime: IN=/path ./run_pipeline.sh)
IN=${IN:-$PROJ/data_in}
SUBJ=$PROJ/config/subjects.json
TASK=$PROJ/config/tasks.json
OUT=$PROJ/results
PROFILE_DEFAULT="V1"
PROFILE="${1:-${PROFILE:-$PROFILE_DEFAULT}}"

# ---- make vars visible to Python ----
export PROJ IN SUBJ TASK OUT PROFILE

# =====================
# Sanity checks
# =====================
[[ -f "$SUBJ" ]] || { echo "ERROR: subjects.json not found at $SUBJ" >&2; exit 1; }
[[ -f "$TASK" ]] || { echo "ERROR: tasks.json not found at $TASK" >&2; exit 1; }
[[ -d "$IN"  ]]  || { echo "ERROR: dataset path IN='$IN' does not exist." >&2; exit 1; }

mkdir -p "$OUT"

# =====================
# Step 00 — Split DWI shells (host Python, idempotent)
# =====================
echo "=== [Step 00] Split DWI shells ==="
python3 - <<'PY'
import os, json, subprocess, sys, glob, time

proj = os.environ["PROJ"]
IN = os.environ["IN"]
OUT = os.environ["OUT"]
subj_json = os.environ["SUBJ"]

with open(subj_json) as f:
    j = json.load(f)

def iter_subjects(j):
    # {"patients":{"sub-PR08":["ses-20250723"], ...}}
    if isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            for s in sess:
                yield sid, s
        return
    # {"subjects":[{"id":"sub-PR08","sessions":["ses-20250723"]}, ...]}
    if isinstance(j, dict) and "subjects" in j:
        for rec in j["subjects"]:
            sid = rec.get("id")
            for s in rec.get("sessions", []):
                yield sid, s

def needs_split(session_dir, out_dir):
    dwi = os.path.join(session_dir, "dwi", "dwi.nii.gz")
    if not os.path.isfile(dwi):
        print(f"[WARN] Missing DWI: {dwi} — skipping split", file=sys.stderr)
        return False
    stamp = os.path.join(out_dir, ".done")
    if os.path.isfile(stamp):
        print(f"[skip] {out_dir} already split (stamp found).")
        return False
    # If any split outputs exist, you can also choose to skip.
    # Uncomment to also skip when split files exist:
    # if glob.glob(os.path.join(out_dir, "dwi_b*.nii.gz")):
    #     print(f"[skip] {out_dir} appears already split (files present).")
    #     return False
    return True

for sid, ses in iter_subjects(j):
    sess_dir = os.path.join(IN, sid, ses)
    out_dir  = os.path.join(OUT, sid, ses, "00-SplitDWIShells")
    os.makedirs(out_dir, exist_ok=True)

    if needs_split(sess_dir, out_dir):
        print(f"[SplitDWIShells] {sid}/{ses}")
        subprocess.run([
            "python3", f"{proj}/SplitDWIShells.py",
            "--session", sess_dir,
            "--outdir", out_dir,
            "--verbose"
        ], check=True)
        # write stamp
        open(os.path.join(out_dir, ".done"), "w").write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n")
    else:
        print(f"[SplitDWIShells] {sid}/{ses} — already done.")
PY

# =====================
# Step 01+ — Run the main Ginkgo pipeline inside container
# =====================
echo "=== [Ginkgo Pipeline] Running in container ==="

apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$IN":/data_in \
  --bind "$OUT":/results \
  "$SIF" bash -lc "
    set -e
    python3 /work/Myproject.py \
      -i /data_in \
      -s /work/config/subjects.json \
      -t /work/config/tasks.json \
      -p $PROFILE \
      -o /results \
      --verbose
  "
