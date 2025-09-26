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
# Step 00 — Split DWI shells (host Python)
# =====================
echo "=== [Step 00] Split DWI shells ==="
python3 - <<'PY'
import os, json, subprocess

proj = os.environ["PROJ"]
IN = os.environ["IN"]
OUT = os.environ["OUT"]
subj_json = os.environ["SUBJ"]

with open(subj_json) as f:
    j = json.load(f)

def iter_subjects(j):
    if isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            for s in sess:
                yield sid, s
    elif isinstance(j, dict) and "subjects" in j:
        for r in j["subjects"]:
            sid = r.get("id")
            for s in r.get("sessions", []):
                yield sid, s

for sid, ses in iter_subjects(j):
    sess_dir = os.path.join(IN, sid, ses)
    out_dir  = os.path.join(OUT, sid, ses, "00-SplitDWIShells")
    os.makedirs(out_dir, exist_ok=True)
    print(f"[SplitDWIShells] {sid}/{ses}")
    subprocess.run([
        "python3", f"{proj}/SplitDWIShells.py",
        "--session", sess_dir,
        "--outdir", out_dir,
        "--verbose"
    ], check=True)
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

