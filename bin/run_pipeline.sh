#!/bin/bash
set -euo pipefail

# ---- Project & container (Wynton) ----
PROJ=/wynton/scratch/aleberre/projects/Ginkgo_pipeline
SIF=/wynton/scratch/aleberre/containers/ginkgobv.sif

# ---- Dataset root (BIDS) ----
# Override at runtime with: IN=/path/to/BIDS ./run_pipeline.sh
IN=${IN:-/wynton/scratch/aleberre/projects/Ginkgo_pipeline/data_in}

# ---- Configs & outputs ----
SUBJ=$PROJ/config/subjects.json
TASK=$PROJ/config/tasks.json
OUT=$PROJ/results

# ---- Timepoint(s) / session(s) ----
PROFILE_DEFAULT="V1"
PROFILE="${1:-${PROFILE:-$PROFILE_DEFAULT}}"

# ---- Guards ----
[[ -f "$SUBJ" ]] || { echo "ERROR: subjects.json not found at $SUBJ" >&2; exit 1; }
[[ -f "$TASK" ]] || { echo "ERROR: tasks.json not found at $TASK" >&2; exit 1; }
[[ -d "$IN"  ]]  || { echo "ERROR: dataset path IN='$IN' does not exist." >&2; exit 1; }

mkdir -p "$OUT"

# ---- Run inside the container ----
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$IN":/data_in \
  --bind "$OUT":/results \
  "$SIF" bash -lc '
    python3 /work/Myproject.py \
      -i /data_in \
      -s /work/config/subjects.json \
      -t /work/config/tasks.json \
      -p '"$PROFILE"' \
      -o /results \
      -v
  '
