#!/bin/bash
set -euo pipefail

# --- Paths (override via env if needed) ---
PROJ=${PROJ:-/wynton/scratch/aleberre/projects/Ginkgo_pipeline}
SIF=${SIF:-/wynton/scratch/aleberre/containers/ginkgobv.sif}
IN_QSI=${IN_QSI:-/wynton/protected/group/rsl/PRESIDIO/data/BIDS/derivatives/qsiprep}
IN_SUBJ_JSON=${IN_SUBJ_JSON:-$PROJ/config/subjects.json}
TASK=${TASK:-$PROJ/config/tasks_qsiprep.json}
OUT=${OUT:-$PROJ/results}
PROFILE_DEFAULT="V1"
PROFILE="${1:-${PROFILE:-$PROFILE_DEFAULT}}"

export PROJ OUT IN_QSI IN_SUBJ_JSON

echo "=== [QSIPrep Alt] IN_QSI=$IN_QSI  OUT=$OUT  PROFILE=$PROFILE"
mkdir -p "$OUT"

# ---------- Stage QSIPrep outputs into 02-Preproc ----------
python3 - <<'PY'
import os, json, glob, shutil, sys

PROJ = os.environ["PROJ"]
OUT  = os.environ["OUT"]
IN_QSI = os.environ["IN_QSI"]
IN_SUBJ_JSON = os.environ["IN_SUBJ_JSON"]

def pick_first(*patterns):
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    return None

with open(IN_SUBJ_JSON, "r") as f:
    subjects = json.load(f)

def iter_subj_ses(j):
    if isinstance(j, dict) and "subjects" in j:
        for rec in j["subjects"]:
            sid = rec.get("id")
            for ses in rec.get("sessions", []):
                yield sid, ses
    elif isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            for ses in sess: yield sid, ses

for sid, ses in iter_subj_ses(subjects):
    dwi_dir  = os.path.join(IN_QSI, sid, ses, "dwi")
    anat_dir = os.path.join(IN_QSI, sid, ses, "anat")
    if not os.path.isdir(dwi_dir):
        print(f"[WARN] No QSIPrep dwi dir for {sid}/{ses}: {dwi_dir}"); continue

    # Prefer space-T1w, else fallback to space-ACPC
    dwi_nii  = pick_first(
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.nii.gz"),
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.nii.gz"),
    )
    dwi_bval = pick_first(
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.bval"),
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.bval"),
    )
    dwi_bvec = pick_first(
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_dwi.bvec"),
        os.path.join(dwi_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_dwi.bvec"),
    )
    # Mask is typically in anat; try anat first, then dwi
    brain_mask = pick_first(
        os.path.join(anat_dir, f"{sid}_{ses}_*space-T1w*_desc-brain_mask.nii.gz"),
        os.path.join(anat_dir, f"{sid}_{ses}_*space-ACPC*_desc-brain_mask.nii.gz"),
        os.path.join(dwi_dir,  f"{sid}_{ses}_*space-T1w*_desc-brain_mask.nii.gz"),
        os.path.join(dwi_dir,  f"{sid}_{ses}_*space-ACPC*_desc-brain_mask.nii.gz"),
    )
    # Also T1w preproc (optional but useful for GIS conversion)
    t1w_nii = pick_first(
        os.path.join(anat_dir, f"{sid}_{ses}_*space-T1w*_desc-preproc_T1w.nii.gz"),
        os.path.join(anat_dir, f"{sid}_{ses}_*space-ACPC*_desc-preproc_T1w.nii.gz"),
    )

    if not (dwi_nii and dwi_bval and dwi_bvec):
        print(f"[WARN] Missing QSIPrep preproc trio for {sid}/{ses} in {dwi_dir}")
        continue

    out02 = os.path.join(OUT, sid, ses, "02-Preproc")
    os.makedirs(out02, exist_ok=True)
    shutil.copy2(dwi_nii,  os.path.join(out02, "dwi_preproc.nii.gz"))
    shutil.copy2(dwi_bval, os.path.join(out02, "dwi_preproc.bval"))
    shutil.copy2(dwi_bvec, os.path.join(out02, "dwi_preproc.bvec"))

    # Stash paths for container conversions
    if brain_mask:
        with open(os.path.join(OUT, sid, ses, "_qsiprep_mask.txt"), "w") as f:
            f.write(brain_mask + "\n")
    if t1w_nii:
        with open(os.path.join(OUT, sid, ses, "_qsiprep_t1.txt"), "w") as f:
            f.write(t1w_nii + "\n")

    print(f"[Stage] {sid}/{ses} -> 02-Preproc (mask={'yes' if brain_mask else 'no'}, T1w={'yes' if t1w_nii else 'no'})")
PY

# ---------- Split shells (host; uses the staged 02-Preproc trio) ----------
python3 - <<'PY'
import os, json, subprocess, sys, shutil

OUT  = os.environ["OUT"]
PROJ = os.environ["PROJ"]
IN_SUBJ_JSON = os.environ["IN_SUBJ_JSON"]

with open(IN_SUBJ_JSON) as f:
    subs = json.load(f)

def iter_subj_ses(j):
    if isinstance(j, dict) and "subjects" in j:
        for rec in j["subjects"]:
            sid = rec.get("id")
            for ses in rec.get("sessions", []):
                yield sid, ses
    elif isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            for ses in sess: yield sid, ses

for sid, ses in iter_subj_ses(subs):
    base = os.path.join(OUT, sid, ses)
    src = os.path.join(base, "02-Preproc")
    if not os.path.isfile(os.path.join(src,"dwi_preproc.nii.gz")):
        print(f"[Split] Skip {sid}/{ses} (no preproc trio)")
        continue
    dst = os.path.join(base, "04-SplitDWIShells")
    os.makedirs(dst, exist_ok=True)

    tmp = os.path.join(dst, "_tmp_session", "dwi")
    os.makedirs(tmp, exist_ok=True)
    shutil.copy2(os.path.join(src,"dwi_preproc.nii.gz"), os.path.join(tmp,"dwi.nii.gz"))
    shutil.copy2(os.path.join(src,"dwi_preproc.bval"),   os.path.join(tmp,"dwi.bval"))
    shutil.copy2(os.path.join(src,"dwi_preproc.bvec"),   os.path.join(tmp,"dwi.bvec"))

    subprocess.run([
        "python3", f"{PROJ}/SplitDWIShells.py",
        "--session", os.path.join(dst, "_tmp_session"),
        "--outdir",  dst,
        "--verbose"
    ], check=True)
    print(f"[Split] {sid}/{ses} OK")
PY

# ---------- Convert QSIPrep mask -> GIS & identity transforms (in container) ----------
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$OUT":/results \
  "$SIF" bash -lc '
set -e
export PYTHONPATH="/usr/share/gkg/python:${PYTHONPATH:-}"
python3 - <<PY
import os, sys, subprocess
root="/results"
for sid in os.listdir(root):
    sdir=os.path.join(root,sid)
    if not os.path.isdir(sdir): continue
    for ses in os.listdir(sdir):
        b=os.path.join(sdir,ses)
        if not os.path.isdir(b): continue
        stash=os.path.join(b,"_qsiprep_mask.txt")
        if not os.path.isfile(stash): continue
        with open(stash) as f: mask=f.read().strip()
        # (optional) T1 path if you stashed it, else empty
        t1_stash=os.path.join(b,"_qsiprep_t1.txt")
        t1 = open(t1_stash).read().strip() if os.path.isfile(t1_stash) else ""
        outdir=os.path.join(b,"08-MaskFromMorphologistPipeline")
        os.makedirs(outdir, exist_ok=True)
        cmd=["python3","/work/tools/qsiprep_mask_to_gis.py",
             "--qsiprep_mask", mask,
             "--outdir", outdir,
             "--verbose"]
        if t1:
            cmd.extend(["--qsiprep_t1", t1])
        subprocess.run(cmd, check=True)
        print(f"[Mask→GIS] {sid}/{ses}")
PY
'
# ---------- Create raw-like dwi/ symlinks for RunPipeline input check ----------
python3 - <<'PY'
import os, json, sys

OUT  = os.environ["OUT"]
with open(os.environ["IN_SUBJ_JSON"], "r") as f:
    subjects = json.load(f)

def iter_subj_ses(j):
    if isinstance(j, dict) and "subjects" in j:
        for rec in j["subjects"]:
            sid = rec.get("id")
            for ses in rec.get("sessions", []):
                yield sid, ses
    elif isinstance(j, dict) and "patients" in j:
        for sid, sess in j["patients"].items():
            for ses in sess: yield sid, ses

for sid, ses in iter_subj_ses(subjects):
    base = os.path.join(OUT, sid, ses)
    src  = os.path.join(base, "02-Preproc")
    dst  = os.path.join(base, "dwi")
    dwi  = os.path.join(src, "dwi_preproc.nii.gz")
    bval = os.path.join(src, "dwi_preproc.bval")
    bvec = os.path.join(src, "dwi_preproc.bvec")
    if not (os.path.isfile(dwi) and os.path.isfile(bval) and os.path.isfile(bvec)):
        print(f"[Compat] Missing preproc trio for {sid}/{ses}, skip dwi/ shim"); continue
    os.makedirs(dst, exist_ok=True)
    def link(srcf, name):
        dstf = os.path.join(dst, name)
        try:
            if os.path.islink(dstf) or os.path.exists(dstf):
                os.remove(dstf)
            os.symlink(srcf, dstf)
        except Exception:
            # fallback copy if symlink not allowed
            import shutil; shutil.copy2(srcf, dstf)
    link(dwi,  "dwi.nii.gz")
    link(bval, "dwi.bval")
    link(bvec, "dwi.bvec")
    print(f"[Compat] Linked {sid}/{ses} dwi/ -> 02-Preproc trio")
PY

# ---------- Run the main pipeline in container (early steps OFF) ----------
apptainer exec --cleanenv \
  --bind "$PROJ":/work \
  --bind "$OUT":/results \
  "$SIF" bash -lc "
  set -e
  export PYTHONPATH=\"/usr/share/gkg/python:\${PYTHONPATH:-}\"
  python3 /work/Myproject.py \
    -i /results \
    -s /work/config/subjects.json \
    -t /work/config/tasks_qsiprep.json \
    -p $PROFILE \
    -o /results \
    --verbose
"

