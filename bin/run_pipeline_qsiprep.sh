#!/bin/bash
set -euo pipefail

# --- Paths (override via env if needed) ---
PROJ=${PROJ:-/wynton/scratch/aleberre/projects/Ginkgo_pipeline}
SIF=${SIF:-/wynton/scratch/aleberre/containers/ginkgobv.sif}
IN_QSI=${IN_QSI:-/wynton/protected/group/rsl/PRESIDIO/data/BIDS/derivatives/qsiprep}
IN_SUBJ_JSON=${IN_SUBJ_JSON:-$PROJ/config/subjects.json}
TASK=${TASK:-$PROJ/config/tasks_qsiprep.json}
OUT=${OUT:-$PROJ/results}

export PROJ OUT IN_QSI IN_SUBJ_JSON TASK

echo "=== [QSIPrep Alt] IN_QSI=$IN_QSI  OUT=$OUT"  
mkdir -p "$OUT"

# ---------- Read tasks_qsiprep.json -> shell flags ----------
# (Missing keys default to 0/“none”)
eval "$(
python3 - <<'PY'
import json, os, sys
p = os.environ["TASK"]
with open(p) as f: t = json.load(f)

def g(name, default=0):
    v = t.get(name, default)
    try:
        return int(v)
    except Exception:
        return 0

dc = str(t.get("DistortionCorrection","none")).strip().lower()
print(f'DC_MODE="{dc}"')
print(f'DO_EDDY={g("EddyCurrentCorrection",0)}')
print(f'DO_OUTLIER={g("OutlierCorrection",0)}')
print(f'DO_SPLIT={g("SplitDWIShells",0)}')
print(f'DO_GIS={g("GisConversion",0)}')
print(f'DO_ORIENT={g("OrientationAndBValueFileDecoding",0)}')
print(f'DO_QSPACE={g("QSpaceSamplingAddition",0)}')
print(f'DO_MORPHO={g("Morphologist",0)}')
print(f'DO_DTI_B0500={g("LocalModelingDTI-B0500",0)}')
print(f'DO_DTI_B1000={g("LocalModelingDTI-B1000",0)}')
print(f'DO_DTI_B2000={g("LocalModelingDTI-B2000",0)}')
print(f'DO_DTI_B3000={g("LocalModelingDTI-B3000",0)}')
print(f'DO_DTI_MULTI={g("LocalModelingDTI-Multiple-Shell",0)}')
print(f'DO_QBI_B0500={g("LocalModelingQBI-B0500",0)}')
print(f'DO_QBI_B1000={g("LocalModelingQBI-B1000",0)}')
print(f'DO_QBI_B2000={g("LocalModelingQBI-B2000",0)}')
print(f'DO_QBI_B3000={g("LocalModelingQBI-B3000",0)}')
print(f'DO_QBI_MULTI={g("LocalModelingQBI-Multiple-Shell",0)}')
PY
)"

# ---------- Build a clean subject/session list once ----------
python3 - <<'PY'
import os, json, sys
IN_SUBJ_JSON = os.environ["IN_SUBJ_JSON"]
OUT          = os.environ["OUT"]
with open(IN_SUBJ_JSON) as f:
    j = json.load(f)

def iter_subj_ses(j):
    if isinstance(j, dict) and "subjects" in j:
        for rec in j["subjects"]:
            sid = rec.get("id")
            for ses in rec.get("sessions", []):
                if sid and ses: yield sid, ses
    elif isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            if isinstance(sess, list):
                for ses in sess: yield sid, ses

lst = []
for sid, ses in iter_subj_ses(j):
    lst.append(f"{sid}\t{ses}")
print("\n".join(lst))
with open(os.path.join(OUT,"_subject_session_list.tsv"),"w") as f:
    f.write("\n".join(lst)+"\n")
PY

LIST_TSV="$OUT/_subject_session_list.tsv"

# ---------- Stage QSIPrep outputs into 02-Preproc (always) ----------
python3 - <<'PY'
import os, json, glob, shutil
OUT  = os.environ["OUT"]
IN_QSI = os.environ["IN_QSI"]
lst = [ln.strip().split("\t") for ln in open(os.path.join(OUT,"_subject_session_list.tsv")) if ln.strip()]
def pick_first(*patterns):
    import glob
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits: return hits[0]
    return None

for sid, ses in lst:
    dwi_dir  = os.path.join(IN_QSI, sid, ses, "dwi")
    anat_dir = os.path.join(IN_QSI, sid, ses, "anat")
    if not os.path.isdir(dwi_dir):
        print(f"[WARN] No QSIPrep dwi dir for {sid}/{ses}: {dwi_dir}"); continue

    dwi_nii  = pick_first(os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.nii.gz"),
                          os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.nii.gz"))
    dwi_bval = pick_first(os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.bval"),
                          os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.bval"))
    dwi_bvec = pick_first(os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.bvec"),
                          os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.bvec"))
    brain_mask = pick_first(os.path.join(anat_dir, f"{sid}_{ses}_*space-T1w*_desc-brain_mask.nii.gz"),
                            os.path.join(anat_dir, f"{sid}_{ses}_*space-ACPC*_desc-brain_mask.nii.gz"),
                            os.path.join(dwi_dir,  f"{sid}_{ses}_*space-T1w*_desc-brain_mask.nii.gz"),
                            os.path.join(dwi_dir,  f"{sid}_{ses}_*space-ACPC*_desc-brain_mask.nii.gz"))
    t1w_nii = pick_first(os.path.join(anat_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_T1w.nii.gz"),
                         os.path.join(anat_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_T1w.nii.gz"))

    if not (dwi_nii and dwi_bval and dwi_bvec):
        print(f"[WARN] Missing QSIPrep preproc trio for {sid}/{ses} in {dwi_dir}")
        continue

    out02 = os.path.join(OUT, sid, ses, "02-Preproc")
    os.makedirs(out02, exist_ok=True)
    shutil.copy2(dwi_nii,  os.path.join(out02, "dwi_preproc.nii.gz"))
    shutil.copy2(dwi_bval, os.path.join(out02, "dwi_preproc.bval"))
    shutil.copy2(dwi_bvec, os.path.join(out02, "dwi_preproc.bvec"))

    if brain_mask:
        open(os.path.join(OUT, sid, ses, "_qsiprep_mask.txt"),"w").write(brain_mask+"\n")
    if t1w_nii:
        open(os.path.join(OUT, sid, ses, "_qsiprep_t1.txt"),"w").write(t1w_nii+"\n")

    # raw-like dwi/ (relative symlinks) — for RunPipeline input check
    dwi_compat = os.path.normpath(os.path.join(out02, "..", "dwi"))
    os.makedirs(dwi_compat, exist_ok=True)
    for src_name, link_name in [("dwi_preproc.nii.gz","dwi.nii.gz"),
                                ("dwi_preproc.bval","dwi.bval"),
                                ("dwi_preproc.bvec","dwi.bvec")]:
        dst = os.path.join(dwi_compat, link_name)
        if os.path.lexists(dst): os.remove(dst)
        os.symlink(os.path.join("..","02-Preproc",src_name), dst)

    print(f"[Stage] {sid}/{ses} -> 02-Preproc (mask={'yes' if brain_mask else 'no'}, T1w={'yes' if t1w_nii else 'no'})")

PY

# ---------- Split shells (only if requested) ----------
if [[ "${DO_SPLIT}" -eq 1 ]]; then
  python3 - <<'PY'
import os, json, subprocess, shutil
OUT  = os.environ["OUT"]
PROJ = os.environ["PROJ"]
pairs = [ln.strip().split("\t") for ln in open(os.path.join(OUT,"_subject_session_list.tsv")) if ln.strip()]
for sid, ses in pairs:
    base = os.path.join(OUT, sid, ses)
    src  = os.path.join(base, "02-Preproc")
    if not os.path.isfile(os.path.join(src,"dwi_preproc.nii.gz")):
        print(f"[Split] Skip {sid}/{ses} (no preproc trio)"); continue
    dst = os.path.join(base, "04-SplitDWIShells")
    os.makedirs(dst, exist_ok=True)
    tmp = os.path.join(dst, "_tmp_session", "dwi")
    os.makedirs(tmp, exist_ok=True)
    for a,b in [("dwi_preproc.nii.gz","dwi.nii.gz"),
                ("dwi_preproc.bval","dwi.bval"),
                ("dwi_preproc.bvec","dwi.bvec")]:
        shutil.copy2(os.path.join(src,a), os.path.join(tmp,b))
    subprocess.run([
        "python3", f"{PROJ}/SplitDWIShells.py",
        "--session", os.path.join(dst, "_tmp_session"),
        "--outdir",  dst, "--verbose"
    ], check=True)
    print(f"[Split] {sid}/{ses} OK")
PY
fi

# ---------- NIfTI→GIS + gradient injection (only if requested) ----------
if [[ "${DO_GIS}" -eq 1 ]]; then
  apptainer exec --cleanenv \
    --bind "$PROJ":/work \
    --bind "$OUT":/results \
    "$SIF" bash -lc '
set -e
export PYTHONPATH="/usr/share/gkg/python:${PYTHONPATH:-}"

# only iterate subject/sessions from the list
while IFS=$'\t' read -r sid ses; do
  [ -n "$sid" ] && [ -n "$ses" ] || continue
  base="/results/$sid/$ses"
  [ -d "$base" ] || continue
  stash="$base/_qsiprep_mask.txt"
  [ -f "$stash" ] || { echo "[GIS][skip] no mask for $sid/$ses"; continue; }
  mask=$(cat "$stash")
  t1f=""
  [ -f "$base/_qsiprep_t1.txt" ] && t1f=$(cat "$base/_qsiprep_t1.txt")
  outdir="$base/08-MaskFromMorphologistPipeline"; mkdir -p "$outdir"

  python3 /work/tools/qsiprep_mask_to_gis.py --qsiprep_mask "$mask" --outdir "$outdir" ${t1f:+--qsiprep_t1 "$t1f"} --verbose
  echo "[Mask→GIS] $sid/$ses"

  # If SplitDWIShells ran, convert shells to GIS and inject gradients
  if [ -d "$base/04-SplitDWIShells" ]; then
    # Convert shells to GIS (the convert already happened earlier in your flow; keep if needed)
    for tag in b0500 b1000 b2000 b3000; do
      nii="$base/04-SplitDWIShells/dwi_${tag}.nii.gz"
      [ -f "$nii" ] || continue
      python3 - <<PYIN
from PyUpys import CommandFactory
from CopyFileDirectoryRm import removeMinf
import sys
CommandFactory().executeCommand({
  "algorithm":"Nifti2GisConverter",
  "parameters":{"fileNameIn":"$nii","fileNameOut":"$base/05-GisConversion/DWI_${tag}.ima","outputFormat":"gis","ascii":False,"verbose":True},
  "verbose":True
})
removeMinf("$base/05-GisConversion/DWI_${tag}.ima")
PYIN
      # inject gradients if present
      bvec="$base/04-SplitDWIShells/dwi_${tag}.bvec"
      bval="$base/04-SplitDWIShells/dwi_${tag}.bval"
      if [ -f "$bvec" ] && [ -f "$bval" ]; then
        python3 /work/tools/add_gradients_to_ima.py --ima "$base/05-GisConversion/DWI_${tag}.ima" --bvec "$bvec" --bval "$bval"
        echo "[Gradients] $sid/$ses $tag -> $base/05-GisConversion/DWI_${tag}.ima.minf"
      fi
    done
  fi
done < /results/_subject_session_list.tsv
'
fi

# ---------- Run the main pipeline in container ----------
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$OUT":/results \
  "$SIF" bash -lc '
set -e
export PYTHONPATH="/usr/share/gkg/python:${PYTHONPATH:-}"
python3 /work/Myproject.py \
  -i /results \
  -s /work/config/subjects.json \
  -t /work/config/tasks_qsiprep.json \
  -o /results \
  --verbose
'


