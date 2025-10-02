#!/bin/bash
set -euo pipefail

PROJ=/wynton/scratch/aleberre/projects/Ginkgo_pipeline
SIF=/wynton/scratch/aleberre/containers/ginkgobv.sif
IN=${IN:-$PROJ/data_in}
OUT=${OUT:-$PROJ/results}
SUBJ=$PROJ/config/subjects.json
TASK=$PROJ/config/tasks.json
PROFILE_DEFAULT="V1"
PROFILE="${1:-${PROFILE:-$PROFILE_DEFAULT}}"

export PROJ IN OUT SUBJ TASK PROFILE

echo "=== [Env] IN=$IN  OUT=$OUT  PROFILE=$PROFILE"
echo "=== [Env] PROJ=$PROJ  SIF=$SIF"

mkdir -p "$OUT"

# ---------- Step 00 — Susceptibility dispatch (TopUp/Fieldmap) ----------
echo "=== [Step 00] Susceptibility dispatch (TopUp or Fieldmap) ==="

if [[ -n "${FSL_SIF:-}" ]]; then
  # Run FSL commands inside the FSL container, but run Python in the Ginkgo container.
  # Bind host absolute paths to themselves so Python/FSL see the same paths.
  export FSL_PREFIX="apptainer exec --cleanenv \
    --bind $IN:$IN \
    --bind $OUT:$OUT \
    ${FSL_SIF}"
  echo "Using FSL container via FSL_PREFIX."
else
  # No FSL container provided; try host FSL (PATH must contain fslmerge/topup/applytopup)
  command -v topup >/dev/null 2>&1 || {
    echo "ERROR: FSL 'topup' not found on host PATH."
    echo "Hints:"
    echo "  • Set FSL_SIF=/path/to/fsl-*.sif, or"
    echo "  • export FSLDIR=/actual/fsl; export PATH=\"\$FSLDIR/bin:\$PATH\""
    exit 2
  }
  export FSL_PREFIX=""
fi

# Run the dispatcher in Ginkgo container (it imports your Python modules)
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$IN":"$IN" \
  --bind "$OUT":"$OUT" \
  "$SIF" bash -lc "
    set -e
    export FSL_PREFIX='$FSL_PREFIX'
    python3 /work/SusceptibilityDispatcher.py \
      --input_root '$IN' \
      --output_root '$OUT' \
      --subjects_json /work/config/subjects.json \
      --verbose
  "

# ---------- Step 01+ — Main pipeline inside Ginkgo container ----------
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
