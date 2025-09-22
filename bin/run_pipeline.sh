#!/bin/bash
set -euo pipefail

# ---- User paths on Wynton ----
PROJ=/wynton/scratch/aleberre/projects/Ginkgo_pipeline
SIF=/wynton/scratch/aleberre/containers/ginkgobv.sif

# ---- Input dataset ----
# TODO: update this path once you know where the dataset is stored on Wynton.
# If your data ends up being copied into your project, use $PROJ/data_in
IN=/path/to/your/dataset   # <--- FILL THIS IN LATER

# Configs & outputs
SUBJ=$PROJ/config/subjects.json
TASK=$PROJ/config/tasks.json
OUT=$PROJ/results
PROFILE=V3

mkdir -p "$OUT"

# ---- Run inside the container ----
# We bind the whole project at /work so inside the container we can use stable paths.
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$IN":/data_in \
  --bind "$OUT":/results \
  "$SIF" bash -lc '
    /work/src/myproject_entrypoint \
      -i /data_in \
      -s /work/config/subjects.json \
      -t /work/config/tasks.json \
      -p '"$PROFILE"' \
      -o /results \
      --verbose
  '
