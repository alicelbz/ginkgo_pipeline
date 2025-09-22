#!/bin/bash
set -euo pipefail

# ---- Project & container (Wynton) ----
PROJ=/wynton/scratch/aleberre/projects/Ginkgo_pipeline
SIF=/wynton/scratch/aleberre/containers/ginkgobv.sif

# ---- Dataset root (BIDS) ----
# TODO: update this once you know the real path (or override via IN=... at runtime)
IN="${IN:-/path/to/your/dataset}"

# ---- Configs & outputs ----
SUBJ=$PROJ/config/subjects.json
TASK=$PROJ/config/tasks.json
OUT=$PROJ/results

# ---- Timepoint(s) / session(s) ----
# Default to a single scan per subject (V1). Override in two ways:
#   1) env var: PROFILE="V1,V2" run_pipeline.sh
#   2) first arg: run_pipeline.sh V2        (takes precedence over env var)
PROFILE_DEFAULT="V1"
PROFILE="${PROFILE:-$PROFILE_DEFAULT}"
if [[ $# -ge 1 && -n "${1:-}" ]]; then
  PROFILE="$1"
fi

# ---- Guards ----
if [[ ! -f "$SUBJ" ]]; then
  echo "ERROR: subjects.json not found at $SUBJ" >&2; exit 1
fi
if [[ ! -f "$TASK" ]]; then
  echo "ERROR: tasks.json not found at $TASK" >&2; exit 1
fi
if [[ ! -d "$IN" ]]; then
  echo "ERROR: dataset path IN='$IN' does not exist. Set IN to your BIDS root and retry." >&2; exit 1
fi

mkdir -p "$OUT"

# ---- Run inside the container ----
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$IN":/data_in \
  --bind "$OUT":/results \
  "$SIF" bash -lc '
    /home/leberre/myproject/myproject \
      -i /data_in \
      -s /work/config/subjects.json \
      -t /work/config/tasks.json \
      -p '"$PROFILE"' \
      -o /results \
      --verbose
  '
