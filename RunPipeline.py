import os, json, sys, shutil, subprocess, glob
import numpy as np

sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import *

import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from CopyFileDirectoryRm import *

from SusceptibilityArtifactFromTopUpCorrection import *
from OrientationAndBValueFileDecoding import *
from QSpaceSamplingAddition import *
from MaskFromMorphologistPipeline import *
from OutlierCorrection import *
from EddyCurrentAndMotionCorrection import *
from LocalModelingDTI import *
from LocalModelingQBI import *
from NoddiMicrostructureField import *
from TractographySRD import *
from FiberLengthHistogramSRD import *
from LongFiberLabelling import *
from ShortFiberLabelling import *
from FreeSurferParcellation import *
from DiffusionMetricsAlongBundles import *
from DiffusionMetricsAlongCutExtremitiesBundles import *
from DiffusionMetricsInROIs import *
from DiffusionMetricsInHippROIs import *
from FastSegmentation import *
from DiffusionMetricsInWhiteGreyMatter import *
from Normalization import *
from ConnectivityMatrix import *
from FullConnectivityTemplate import *
from DiffusionMetricsInHippocampiConnectivityTemplate import *
from DiffusionMetricsInFullConnectivityTemplate import *
from DiffusionMetricsInConnectivityMatrix import *
from DiffusionMetricsInMNISpace import *
from DiffusionMetricsInCutExtremitiesConnectivityMatrix import *

from NiftiToGisConversion import runNifti2GisConversion
from FieldmapCorrection import runFieldmapCorrection

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def _safe(task_dict, key, default=0):
    try:
        return int(task_dict.get(key, default))
    except Exception:
        return default

def _ensure_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    return d

def makeDirectory(root, name):
    return _ensure_dir(os.path.join(root, name))

def _subjects_from_json(subjects_json):
    """
    Yield (subject_id, session_id) for flexible subjects.json formats:
    A) {"subjects":[{"id":"sub-XX","sessions":["ses-YYYYMMDD"]}, ...]}
    B) {"patients":{"sub-XX":["ses-..."], ...}}
    C) {"patients":{"sub-XX":{"sessions":[...]}, ...}}
    D) {"patients":["sub-XX","sub-YY"]}  # no sessions
    """
    # A
    if isinstance(subjects_json, dict) and isinstance(subjects_json.get("subjects"), list):
        for rec in subjects_json["subjects"]:
            sid = rec.get("id")
            sessions = rec.get("sessions", [])
            if sid and sessions:
                for ses in sessions:
                    yield sid, ses
            elif sid:
                yield sid, None
        return
    # B/C/D under arbitrary group keys
    for _, entries in subjects_json.items():
        if isinstance(entries, list) and all(isinstance(x, str) for x in entries):
            for sid in entries:
                yield sid, None
            continue
        if isinstance(entries, dict):
            for sid, meta in entries.items():
                if isinstance(meta, list) and all(isinstance(x, str) for x in meta):
                    for ses in meta:
                        yield sid, ses
                elif isinstance(meta, dict) and isinstance(meta.get("sessions"), list):
                    for ses in meta["sessions"]:
                        yield sid, ses
                else:
                    yield sid, None

def _json_load(p):
    try:
        with open(p, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def _distortion_method_auto(session_dir):
    """
    Detects:
    - 'topup' if fmap/AP.json + fmap/PA.json with opposite PhaseEncodingDirection,
    - 'fieldmap' if phasediff + magnitude(s),
    - None otherwise.
    """
    fmap = os.path.join(session_dir, 'fmap')
    if not os.path.isdir(fmap):
        return None

    # TopUp: AP/PA pair (EPI b0s)
    ap_json = os.path.join(fmap, 'AP.json')
    pa_json = os.path.join(fmap, 'PA.json')
    if os.path.isfile(ap_json) and os.path.isfile(pa_json):
        ap = _json_load(ap_json).get("PhaseEncodingDirection")
        pa = _json_load(pa_json).get("PhaseEncodingDirection")
        axes = {"i","i-","j","j-","k","k-"}
        if ap in axes and pa in axes and ap != pa:
            return "topup"

    # Fieldmap: phasediff + magnitude(s)
    phasediff = glob.glob(os.path.join(fmap, "*phasediff*.nii*"))
    mag = glob.glob(os.path.join(fmap, "*magnitude*.nii*"))
    if phasediff and mag:
        return "fieldmap"

    return None

def _pick_distortion_method(taskDescription, session_dir):
    """
    Priority:
    1) tasks.json: DistortionCorrection ∈ {'topup','fieldmap'}
    2) legacy flags: TopUpCorrection==1 or FieldmapCorrection==1
    3) auto-detect
    """
    dc = str(taskDescription.get("DistortionCorrection", "")).strip().lower()
    if dc in ("topup", "fieldmap"):
        return dc
    if _safe(taskDescription, "TopUpCorrection", 0) == 1:
        return "topup"
    if _safe(taskDescription, "FieldmapCorrection", 0) == 1:
        return "fieldmap"
    return _distortion_method_auto(session_dir)

def _attach_gradients_to_gis(ima_path, bval_path, bvec_path, verbose=False):
    """
    Attach gradients to a GIS volume by writing MINF sidecars:
      - <basename>.dim.minf  [PRIMARY for GIS]
      - <basename>.minf      [extra]
      - <basename>.ima.minf  [extra]
    Attributes:
      'diffusion_gradient_orientations' : [ [gx,gy,gz], ... ]
      'diffusion_b_values'              : [ b1, b2, ... ]
    """
    # Read bvecs (3 rows: x, y, z)
    with open(bvec_path, "r") as f:
        rows = [ln.strip().split() for ln in f if ln.strip()]
    if len(rows) < 3:
        raise RuntimeError(f"Invalid .bvec format: {bvec_path}")

    grads = list(map(list, zip(*[[float(x) for x in row] for row in rows])))

    # Read bvals
    with open(bval_path, "r") as f:
        bvals = [float(x) for x in f.read().strip().split()]

    if len(bvals) != len(grads):
        raise RuntimeError(
            f"bval/bvec length mismatch: {len(bvals)} vs {len(grads)} "
            f"({bval_path} / {bvec_path})"
        )

    attrs = {
        'diffusion_gradient_orientations': grads,
        'diffusion_b_values': bvals,
    }
    body = "attributes = " + repr(attrs) + "\n"

    base, ext = os.path.splitext(ima_path)         # base=/.../DWI_b0500 , ext=.ima
    minf_dim  = base + ".dim.minf"                 # PRIMARY for GIS
    minf_raw  = base + ".minf"                     # extra
    minf_ima  = ima_path + ".minf"                 # extra

    for p in (minf_dim, minf_raw, minf_ima):
        with open(p, "w") as f:
            f.write(body)
        if verbose:
            print(f"[Attach] wrote {os.path.basename(p)}")

def assert_gis_has_gradients(ima_path, label):
    """Crash early with a clear message if .dim.minf is missing required keys."""
    base, _ = os.path.splitext(ima_path)
    dim_minf = base + ".dim.minf"
    if not os.path.isfile(dim_minf):
        raise RuntimeError(f"[MINF] Missing {dim_minf} for {label}")
    ns = {}
    with open(dim_minf, "r") as f:
        exec(f.read(), ns)
    attrs = ns.get("attributes", {})
    if "diffusion_gradient_orientations" not in attrs:
        raise RuntimeError(f"[MINF] {dim_minf} missing diffusion_gradient_orientations for {label}")


# ---------------------------------------------------------------------
# Main pipeline (NIfTI input only; GIS only where reference pipeline used it)
# ---------------------------------------------------------------------
    # session_id is just the BIDS session (e.g., ses-20241220)

def runPipeline(inputNiftiRoot, subjectJsonFileName, taskJsonFileName, session, outputDirectory, verbose):
    _ensure_dir(outputDirectory)

    # Load subjects / tasks
    with open(subjectJsonFileName, "r") as f:
        subjects = json.load(f)
    with open(taskJsonFileName, "r") as f:
        taskDescription = json.load(f)

    # Optional safety: warn if someone accidentally supplied a profiled tasks file
    if any(isinstance(v, dict) for v in taskDescription.values()):
        raise ValueError(
            "tasks_qsiprep.json looks nested (profiles like V1/V2). "
            "This pipeline expects a flat dict of 0/1 flags."
        )


    for subject, ses in _subjects_from_json(subjects):
        if ses is None:
            if verbose:
                print(f"[WARN] No session listed for {subject}; skipping.")
            continue

        if verbose:
            print("===================================================")
            print(f"{subject} / {ses}")
            print("===================================================")

        # --- Input check (NIfTI) ---
        session_dir  = os.path.join(inputNiftiRoot, subject, ses)
        if not os.path.isdir(session_dir):
            if verbose: print(f"[WARN] Missing session dir: {session_dir} -> skip.")
            continue

        dwi_dir      = os.path.join(session_dir, "dwi")
        dwi_4d       = os.path.join(dwi_dir, "dwi.nii.gz")
        bval_4d      = os.path.join(dwi_dir, "dwi.bval")
        bvec_4d      = os.path.join(dwi_dir, "dwi.bvec")
        if not (os.path.isfile(dwi_4d) and os.path.isfile(bval_4d) and os.path.isfile(bvec_4d)):
            print(f"[WARN] Missing DWI inputs in {session_dir}; skipping.")
            continue

        # --- Output directory scaffold per subject/session ---
        subj_out = _ensure_dir(os.path.join(outputDirectory, subject, ses))
        dir01_dc      = makeDirectory(subj_out, "01-DistortionCorrection")
        dir02_eddy    = makeDirectory(subj_out, "02-Eddy")
        dir03_outlier = makeDirectory(subj_out, "03-OutlierCorrection")
        dir04_split   = makeDirectory(subj_out, "04-SplitDWIShells")
        dir05_gis     = makeDirectory(subj_out, "05-GisConversion")
        dir06_orient  = makeDirectory(subj_out, "06-OrientationAndBValueFileDecoding")
        dir07_qs      = makeDirectory(subj_out, "07-QSpaceSamplingAddition")
        dir08_morph   = makeDirectory(subj_out, "08-MaskFromMorphologistPipeline")
        
        subjectOutputDirectory = subj_out  

        # -----------------------------------------------------------------
        # 01) Distortion correction (TopUp OR Fieldmap OR passthrough)
        # -----------------------------------------------------------------
        method  = _pick_distortion_method(taskDescription, session_dir)  # "topup" | "fieldmap" | None
        if verbose:
            print(f"[01] DistortionCorrection method = {method or 'none (skip)'}")

        dwi_dc   = os.path.join(dir01_dc, "dwi_dc.nii.gz")
        bval_dc  = os.path.join(dir01_dc, "dwi_dc.bval")
        bvec_dc  = os.path.join(dir01_dc, "dwi_dc.bvec")

        did_dc = False
        if method == "topup" and _safe(taskDescription, "DistortionCorrection", 1) != 0:
            runTopUpCorrection(session_dir, dir01_dc, verbose)
            maybe = os.path.join(dir01_dc, "dwi_topup.nii.gz")
            if os.path.isfile(maybe) and not os.path.isfile(dwi_dc):
                shutil.move(maybe, dwi_dc)
            shutil.copy2(bval_4d, bval_dc)
            shutil.copy2(bvec_4d, bvec_dc)
            did_dc = os.path.isfile(dwi_dc)

        elif method == "fieldmap" and _safe(taskDescription, "DistortionCorrection", 1) != 0:
            runFieldmapCorrection(
                subjectSessionDir=session_dir,
                dwi=dwi_4d, bval=bval_4d, bvec=bvec_4d,
                outDir=dir01_dc, verbose=verbose
            )
            if not os.path.isfile(bval_dc): shutil.copy2(bval_4d, bval_dc)
            if not os.path.isfile(bvec_dc): shutil.copy2(bvec_4d, bvec_dc)
            did_dc = os.path.isfile(dwi_dc)

        else:
            # explicit "none" OR task flag disabled -> passthrough
            shutil.copy2(dwi_4d,  dwi_dc)
            shutil.copy2(bval_4d, bval_dc)
            shutil.copy2(bvec_4d, bvec_dc)
            did_dc = True

        if not did_dc:
            print("[ERROR] Distortion correction did not produce dwi_dc.nii.gz; skipping.")
            continue

        # -----------------------------------------------------------------
        # 02) Eddy (rotates bvecs internally)
        # -----------------------------------------------------------------
        dwi_preproc  = os.path.join(dir02_eddy, "dwi_preproc.nii.gz")
        bval_preproc = os.path.join(dir02_eddy, "dwi_preproc.bval")
        bvec_preproc = os.path.join(dir02_eddy, "dwi_preproc.bvec")

        if _safe(taskDescription, "EddyCurrentCorrection", 0) == 1:
            runEddyCurrentAndMotionCorrection(
                inputDirectory=dir01_dc,     # expects dwi_dc + bval/bvec
                outputDirectory=dir02_eddy,
                verbose=verbose
            )
            # Ensure grads are present:
            if not os.path.isfile(bval_preproc): shutil.copy2(bval_dc, bval_preproc)
            if not os.path.isfile(bvec_preproc): shutil.copy2(bvec_dc, bvec_preproc)
        else:
            shutil.copy2(dwi_dc,  dwi_preproc)
            shutil.copy2(bval_dc, bval_preproc)
            shutil.copy2(bvec_dc, bvec_preproc)

        if not os.path.isfile(dwi_preproc):
            print("[ERROR] Eddy step missing dwi_preproc.nii.gz; skipping.")
            continue

        # -----------------------------------------------------------------
        # 03) Optional extra OutlierCorrection (you can skip if eddy --repol)
        # -----------------------------------------------------------------
        use_extra_outlier = (_safe(taskDescription, "OutlierCorrection", 0) == 1)
        if use_extra_outlier:
            runOutlierCorrection(
                inputDirectory=dir02_eddy,
                outputDirectory=dir03_outlier,
                verbose=verbose
            )
            dwi_ready  = (os.path.join(dir03_outlier, "dwi_outliercorr.nii.gz")
                        if os.path.isfile(os.path.join(dir03_outlier, "dwi_outliercorr.nii.gz"))
                        else dwi_preproc)
            bval_ready = bval_preproc
            bvec_ready = bvec_preproc
        else:
            dwi_ready, bval_ready, bvec_ready = dwi_preproc, bval_preproc, bvec_preproc

        # -----------------------------------------------------------------
        # 04) Split shells (on corrected 4D) → still NIfTI here
        #     (guarded by SplitDWIShells flag; skip if already present)
        # -----------------------------------------------------------------
        do_split = (_safe(taskDescription, "SplitDWIShells", 0) == 1)
        have_split = bool(glob.glob(os.path.join(dir04_split, "dwi_b*.nii.gz")))

        if do_split and not have_split:
            tmp_session = os.path.join(dir04_split, "_tmp_session")
            _ensure_dir(os.path.join(tmp_session, "dwi"))
            shutil.copy2(dwi_ready,  os.path.join(tmp_session, "dwi", "dwi.nii.gz"))
            shutil.copy2(bval_ready, os.path.join(tmp_session, "dwi", "dwi.bval"))
            shutil.copy2(bvec_ready, os.path.join(tmp_session, "dwi", "dwi.bvec"))

            # Find SplitDWIShells.py robustly (container mounts your repo at /work)
            split_script = None
            for cand in (
                "/work/SplitDWIShells.py",
                os.path.join(os.path.dirname(__file__), "SplitDWIShells.py"),
                os.path.join(os.getcwd(), "SplitDWIShells.py"),
            ):
                if os.path.isfile(cand):
                    split_script = cand
                    break
            if split_script is None:
                raise FileNotFoundError(
                    "SplitDWIShells.py not found in /work or the current repo. "
                    "Expected at /work/SplitDWIShells.py (bound from your project)."
                )

            subprocess.run([
                "python3", split_script,
                "--session", tmp_session,
                "--outdir",  dir04_split,
                "--verbose"
            ], check=True)
        elif not do_split and verbose:
            print("[04] SplitDWIShells disabled by tasks file.")

        # -----------------------------------------------------------------
        # 05) GIS conversion (per shell) + T1 (guarded by GisConversion flag)
        # -----------------------------------------------------------------
        shell_tags = ["b0000", "b0500", "b1000", "b2000", "b3000"]

        if _safe(taskDescription, "GisConversion", 0) == 1:
            # T1 → GIS (for Morphologist)
            t1_nii = os.path.join(session_dir, "anat", "T1w.nii.gz")
            if os.path.isfile(t1_nii):
                t1_ima = os.path.join(dir05_gis, "T1w.ima")
                CommandFactory().executeCommand({
                    "algorithm": "Nifti2GisConverter",
                    "parameters": {
                        "fileNameIn":  str(t1_nii),
                        "fileNameOut": str(t1_ima),
                        "outputFormat":"gis",
                        "ascii": False,
                        "verbose": verbose
                    },
                    "verbose": verbose
                })
                removeMinf(t1_ima)
            else:
                if verbose: print(f"[WARN] Missing T1: {t1_nii}")

            # DWI per shell → GIS
            for tag in shell_tags:
                nii  = os.path.join(dir04_split, f"dwi_{tag}.nii.gz")
                if not os.path.isfile(nii):
                    continue
                out_ima = os.path.join(dir05_gis, f"DWI_{tag}.ima")
                CommandFactory().executeCommand({
                    "algorithm": "Nifti2GisConverter",
                    "parameters": {
                        "fileNameIn":  str(nii),
                        "fileNameOut": str(out_ima),
                        "outputFormat":"gis",
                        "ascii": False,
                        "verbose": verbose
                    },
                    "verbose": verbose
                })
                # remove auto .minf so we fully control metadata
                removeMinf(out_ima)
        else:
            if verbose: print("[05] GisConversion disabled by tasks file.")

        # -----------------------------------------------------------------
        # 05b) Ensure a T2 surrogate for modeling (use b0 as proxy)
        # -----------------------------------------------------------------
        if _safe(taskDescription, "GisConversion", 0) == 1:
            b0_nii = os.path.join(dir04_split, "dwi_b0000.nii.gz")
            t2_ima = os.path.join(dir04_split, "t2_wo_eddy_current.ima")
            if os.path.isfile(b0_nii) and not os.path.isfile(t2_ima):
                CommandFactory().executeCommand({
                    "algorithm": "Nifti2GisConverter",
                    "parameters": {
                        "fileNameIn":  str(b0_nii),
                        "fileNameOut": str(t2_ima),
                        "outputFormat":"gis",
                        "ascii": False,
                        "verbose": verbose
                    },
                    "verbose": verbose
                })
                # keep .minf: modeling doesn't need one for T2

        # -----------------------------------------------------------------
        # 05c) Attach gradients/bvals to each per-shell GIS (with the CLI tool)
        #     so DwiTensorField finds 'diffusion_gradient_orientations'
        # -----------------------------------------------------------------
        if _safe(taskDescription, "GisConversion", 0) == 1:
            shell_map = {
                "b0500": ("dwi_b0500.bval", "dwi_b0500.bvec", "DWI_b0500.ima",  500.0),
                "b1000": ("dwi_b1000.bval", "dwi_b1000.bvec", "DWI_b1000.ima", 1000.0),
                "b2000": ("dwi_b2000.bval", "dwi_b2000.bvec", "DWI_b2000.ima", 2000.0),
                "b3000": ("dwi_b3000.bval", "dwi_b3000.bvec", "DWI_b3000.ima", 3000.0),
            }
            for tag,(bval_name,bvec_name,ima_name, shell_b) in shell_map.items():
                bval_p = os.path.join(dir04_split, bval_name)
                bvec_p = os.path.join(dir04_split, bvec_name)
                ima_p  = os.path.join(dir05_gis,  ima_name)
                if os.path.isfile(ima_p) and os.path.isfile(bvec_p):
                    # Prefer real bvals if present; else force the shell value
                    cmd = ["python3", "/work/tools/add_gradients_to_ima.py", "--ima", ima_p, "--bvec", bvec_p]
                    if os.path.isfile(bval_p):
                        cmd += ["--bval", bval_p]
                    else:
                        cmd += ["--shell_bvalue", str(shell_b)]
                    try:
                        subprocess.run(cmd, check=True)
                    except Exception as e:
                        print(f"[WARN] Could not attach gradients to {ima_p}: {e}")

        # -----------------------------------------------------------------
        # 06) Orientation & BValue decoding (bridge GIS metadata + NIfTI)
        # -----------------------------------------------------------------
        if _safe(taskDescription, "OrientationAndBValueFileDecoding", 0) == 1:
            runOrientationAndBValueFileDecoding(
                outputDirectoryGisConversion=dir05_gis,     # GIS per-shell + T1
                outputDirectoryTopUpCorrection=dir01_dc,    # NIfTI (dwi_dc + grads) — compat
                flippingTypes=['y'],
                description={},                             # not needed with GIS-per-shell
                outputDirectory=dir06_orient,
                verbose=verbose
            )

        # -----------------------------------------------------------------
        # 07) Q-Space sampling (NIfTI)
        # -----------------------------------------------------------------
        if _safe(taskDescription, "QSpaceSamplingAddition", 0) == 1:
            runQSpaceSamplingAddition(dir06_orient, dir07_qs, verbose)

        # -----------------------------------------------------------------
        # 08) Morphologist (GIS-based)
        # -----------------------------------------------------------------
        if _safe(taskDescription, "Morphologist", 0) == 1:
            runMaskFromMorphologistPipeline(
                dir05_gis,                      # GIS: T1w.ima + DWI shells (if needed)
                dir07_qs,                       # NIfTI gradients q-space (if your func expects)
                os.path.join(dir05_gis, "T1w.APC"),
                dir08_morph,
                verbose
            )


        # -----------------------------
        # Local modeling (single-shell)
        # -----------------------------
        # Per-shell GIS inputs produced earlier:
        dw_ima_0500 = os.path.join(dir05_gis, "DWI_b0500.ima")
        dw_ima_1000 = os.path.join(dir05_gis, "DWI_b1000.ima")
        dw_ima_2000 = os.path.join(dir05_gis, "DWI_b2000.ima")
        dw_ima_3000 = os.path.join(dir05_gis, "DWI_b3000.ima")

        # Where per-shell bval/bvec live (from split step)
        outputDirectoryEddyCurrentAndMotionCorrection = dir04_split   # keeps your function signature happy
        outputDirectoryMaskFromMorphologist = dir08_morph

        # ---- DTI b=500 ----
        outputDirectoryLocalModelingDTIShell1 = makeDirectory(subj_out, "09-LocalModeling-DTI-B0500")
        fileNameDwShell1 = dw_ima_0500
        if os.path.isfile(fileNameDwShell1) and _safe(taskDescription, "LocalModelingDTI-B0500", 0) == 1:
            runLocalModelingDTI(
                fileNameDwShell1,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingDTIShell1,
                verbose
            )

        # ---- DTI b=1000 ----
        outputDirectoryLocalModelingDTIShell2 = makeDirectory(subj_out, "10-LocalModeling-DTI-B1000")
        fileNameDwShell2 = dw_ima_1000
        if os.path.isfile(fileNameDwShell2) and _safe(taskDescription, "LocalModelingDTI-B1000", 0) == 1:
            runLocalModelingDTI(
                fileNameDwShell2,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingDTIShell2,
                verbose
            )

        # ---- DTI b=2000 ----
        outputDirectoryLocalModelingDTIShell3 = makeDirectory(subj_out, "11-LocalModeling-DTI-B2000")
        fileNameDwShell3 = dw_ima_2000
        if os.path.isfile(fileNameDwShell3) and _safe(taskDescription, "LocalModelingDTI-B2000", 0) == 1:
            runLocalModelingDTI(
                fileNameDwShell3,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingDTIShell3,
                verbose
            )

        # ---- DTI b=3000 ----
        outputDirectoryLocalModelingDTIShell4 = makeDirectory(subj_out, "12-LocalModeling-DTI-B3000")
        fileNameDwShell4 = dw_ima_3000
        if os.path.isfile(fileNameDwShell4) and _safe(taskDescription, "LocalModelingDTI-B3000", 0) == 1:
            runLocalModelingDTI(
                fileNameDwShell4,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingDTIShell4,
                verbose
            )

        # --------------------------------
        # (Optional) DTI Multi-shell block
        # --------------------------------
        # If your runLocalModelingDTI supports a multi-shell input, you likely need a merged GIS or a config
        # that points to multiple shells. If not ready, you can leave this disabled for now.
        outputDirectoryLocalModelingDTIMultipleShell = makeDirectory(subj_out, "13-LocalModeling-DTI-Multiple-Shell")
        if _safe(taskDescription, "LocalModelingDTI-Multiple-Shell", 0) == 1:
            # TODO: adapt to your expected multi-shell input format.
            # Example (pseudo): runLocalModelingDTI_Multi([dw_ima_0500, dw_ima_1000, dw_ima_2000, dw_ima_3000], ...)
            pass

        # -----------------------------
        # QBI (single-shell examples)
        # -----------------------------
        outputDirectoryLocalModelingQBIShell1 = makeDirectory(subj_out, "14-LocalModeling-QBI-B0500")
        if os.path.isfile(dw_ima_0500) and _safe(taskDescription, "LocalModelingQBI-B0500", 0) == 1:
            runLocalModelingQBI(
                dw_ima_0500,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingQBIShell1,
                verbose
            )

        outputDirectoryLocalModelingQBIShell2 = makeDirectory(subj_out, "15-LocalModeling-QBI-B1000")
        if os.path.isfile(dw_ima_1000) and _safe(taskDescription, "LocalModelingQBI-B1000", 0) == 1:
            runLocalModelingQBI(
                dw_ima_1000,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingQBIShell2,
                verbose
            )

        outputDirectoryLocalModelingQBIShell3 = makeDirectory(subj_out, "16-LocalModeling-QBI-B2000")
        if os.path.isfile(dw_ima_2000) and _safe(taskDescription, "LocalModelingQBI-B2000", 0) == 1:
            runLocalModelingQBI(
                dw_ima_2000,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingQBIShell3,
                verbose
            )

        outputDirectoryLocalModelingQBIShell4 = makeDirectory(subj_out, "17-LocalModeling-QBI-B3000")
        if os.path.isfile(dw_ima_3000) and _safe(taskDescription, "LocalModelingQBI-B3000", 0) == 1:
            runLocalModelingQBI(
                dw_ima_3000,
                outputDirectoryEddyCurrentAndMotionCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryLocalModelingQBIShell4,
                verbose
            )

        # --------------------------------
        # QBI Multi-shell block
        # --------------------------------
        outputDirectoryLocalModelingQBIMultipleShell = makeDirectory(subj_out, "18-LocalModeling-QBI-Multiple-Shell")
        if _safe(taskDescription, "LocalModelingQBI-Multiple-Shell", 0) == 1:
            # TODO: adapt to your expected multi-shell input format.
            pass

        # -----------------------------
        # NODDI (multi-shell typically)
        # -----------------------------
        outputDirectoryMicrostructureField = makeDirectory(subj_out, "19-NoddiMicrostructureField")
        if _safe(taskDescription, "NoddiMicrostructureField", 0) == 1:
            # If your NODDI code expects the corrected 4D + bval/bvec, point it to dir02_eddy or dir03_outlier.
            # If it expects per-shell GIS, adapt similarly to DTI/QBI above.
            runNoddiMicrostructureField(
                dir02_eddy,                         # or dir03_outlier if you enabled extra outlier correction
                outputDirectoryMaskFromMorphologist,
                outputDirectoryMicrostructureField,
                verbose
            )

        # -----------------------------
        # Tractography (example wiring)
        # -----------------------------
        outputDirectoryTractographySRD = makeDirectory(subj_out, "20-Tractography-SRD")
        if _safe(taskDescription, "TractographySRD", 0) == 1:
            # Example: use the QBI b=2000 outputs (as you did before)
            runTractographySRD(
                outputDirectoryLocalModelingQBIShell3,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryTractographySRD,
                verbose
            )


        ################################################################
        # running fiber length histogram with SRD tractogram
        ################################################################

        outputDirectoryFiberLengthHistogramSRD = \
                            makeDirectory( subjectOutputDirectory,
                                            "20-FiberLengthHistogram-SRD" )

        if _safe(taskDescription, "FiberLengthHistogramSRD", 0) == 1:
            runFiberLengthHistogramSRD( 
                                    outputDirectoryTractographySRD,
                                    outputDirectoryFiberLengthHistogramSRD,
                                    verbose )

        ################################################################
        # running long fiber labelling from SRD tractogram
        ################################################################

        outputDirectoryLongFiberLabellingSRD = makeDirectory( \
                                                subjectOutputDirectory,
                                                "21-LongFiberLabellingSRD")

        if _safe(taskDescription, "LongFiberLabellingSRD", 0) == 1:
            runLongFiberLabelling( outputDirectoryTractographySRD,
                                    outputDirectoryMaskFromMorphologist,
                                    outputDirectoryLongFiberLabellingSRD,
                                    verbose )

        ################################################################
        # running short fiber labelling from SRD tractogram
        ################################################################

        outputDirectoryShortFiberLabellingSRD = makeDirectory( \
                                            subjectOutputDirectory,
                                            "22-ShortFiberLabellingSRD")

        if _safe(taskDescription, "ShortFiberLabellingSRD", 0) == 1:
            runShortFiberLabelling( outputDirectoryTractographySRD,
                                    outputDirectoryMaskFromMorphologist,
                                    outputDirectoryShortFiberLabellingSRD,
                                    verbose )
                                    

        ################################################################
        # computing diffusion metrics along long bundles SRD
        ################################################################

        outputDirectoryDiffusionMetricsAlongLongBundlesSRD = \
            makeDirectory( subjectOutputDirectory,
                            "23-DiffusionMetricsAlongLongBundlesSRD" )

        if _safe(taskDescription, "DiffusionMetricsAlongLongBundlesSRD", 0) == 1:
            runDiffusionMetricsAlongBundles( 
                        outputDirectoryLongFiberLabellingSRD,
                        outputDirectoryLocalModelingDTIMultipleShell,
                        outputDirectoryLocalModelingQBIMultipleShell,
                        outputDirectoryMicrostructureField,
                        outputDirectoryMaskFromMorphologist,
                        outputDirectoryDiffusionMetricsAlongLongBundlesSRD,
                        verbose )

        ################################################################
        # computing diffusion metrics along long bundles SRD
        ################################################################

        outputDirectoryDiffusionMetricsAlongCutExtremitiesLongBundlesSRD = \
            makeDirectory( subjectOutputDirectory,
                            "23-DiffusionMetricsAlongCutExtremitiesLongBundlesSRD" )

        if ( taskDescription[ 
            "DiffusionMetricsAlongCutExtremitiesLongBundlesSRD" ] == 1 ):

            runDiffusionMetricsAlongCutExtremitiesBundles( 
                        outputDirectoryLongFiberLabellingSRD,
                        outputDirectoryLocalModelingDTIMultipleShell,
                        outputDirectoryLocalModelingQBIMultipleShell,
                        outputDirectoryMicrostructureField,
                        outputDirectoryMaskFromMorphologist,
                        outputDirectoryDiffusionMetricsAlongCutExtremitiesLongBundlesSRD,
                        verbose )

        ################################################################
        # computing diffusion metrics along short bundles SRD
        ################################################################

        outputDirectoryDiffusionMetricsAlongShortBundlesSRD = \
            makeDirectory( subjectOutputDirectory,
                            "24-DiffusionMetricsAlongShortBundlesSRD" )

        if ( taskDescription[ 
                        "DiffusionMetricsAlongShortBundlesSRD" ] == 1 ):

            runDiffusionMetricsAlongBundles( 
                    outputDirectoryShortFiberLabellingSRD,
                    outputDirectoryLocalModelingDTIMultipleShell,
                    outputDirectoryLocalModelingQBIMultipleShell,
                    outputDirectoryMicrostructureField,
                    outputDirectoryMaskFromMorphologist,
                    outputDirectoryDiffusionMetricsAlongShortBundlesSRD,
                    verbose )

        ################################################################
        # computing diffusion metrics along short bundles SRD
        ################################################################

        outputDirectoryDiffusionMetricsAlongCutExtremitiesShortBundlesSRD = \
            makeDirectory( subjectOutputDirectory,
                            "24-DiffusionMetricsAlongCutExtremitiesShortBundlesSRD" )

        if ( taskDescription[ 
                        "DiffusionMetricsAlongCutExtremitiesShortBundlesSRD" ] == 1 ):

            runDiffusionMetricsAlongCutExtremitiesBundles( 
                    outputDirectoryShortFiberLabellingSRD,
                    outputDirectoryLocalModelingDTIMultipleShell,
                    outputDirectoryLocalModelingQBIMultipleShell,
                    outputDirectoryMicrostructureField,
                    outputDirectoryMaskFromMorphologist,
                    outputDirectoryDiffusionMetricsAlongCutExtremitiesShortBundlesSRD,
                    verbose )

        ################################################################
        # running freesurfer parcellation
        ################################################################

        outputDirectoryFreeSurferParcellation = makeDirectory(
                                            subjectOutputDirectory,
                                            "25-FreeSurferParcellation")

        if ( taskDescription["FreesurferParcellation"] == 1 ):

            runFreeSurferParcellation(
                                    outputDirectoryMaskFromMorphologist,
                                    subject,
                                    outputDirectoryFreeSurferParcellation,
                                    verbose )

        ################################################################
        # computing diffusion metrics in FreeSurfer ROIs
        ################################################################

        outputDirectoryDiffusionMetricsInROIs = makeDirectory(
                                            subjectOutputDirectory,
                                            "26-DiffusionMetricsInROIs" )

        if ( taskDescription[ "DiffusionMetricsInROIs" ] == 1 ):

            runDiffusionMetricsInROIs( 
                            outputDirectoryFreeSurferParcellation,
                            outputDirectoryLocalModelingDTIMultipleShell,
                            outputDirectoryLocalModelingQBIMultipleShell,
                            outputDirectoryMicrostructureField,
                            outputDirectoryMaskFromMorphologist,
                            outputDirectoryDiffusionMetricsInROIs,
                            verbose )

        ################################################################
        # running fast segmentation
        ################################################################

        outputDirectoryFastSegmentation = makeDirectory(
                                                    subjectOutputDirectory,
                                                    "27-FastSegmentation")

        if (taskDescription["FastSegmentation"] == 1):

            runFASTSegmentation( outputDirectoryMaskFromMorphologist,
                                outputDirectoryFastSegmentation,
                                verbose )

        ################################################################
        # computing diffusion metrics in white and grey matter
        ################################################################

        outputDirectoryDiffusionMetricsInWhiteGreyMatter = \
            makeDirectory( subjectOutputDirectory,
                            "28-DiffusionMetricsInWhiteGreyMatter" )

        if ( taskDescription[ 
                            "DiffusionMetricsInWhiteGreyMatter" ] == 1 ):

            runDiffusionMetricsInWhiteGreyMatter( 
                        outputDirectoryFastSegmentation,
                        outputDirectoryLocalModelingDTIMultipleShell,
                        outputDirectoryLocalModelingQBIMultipleShell,
                        outputDirectoryMicrostructureField,
                        outputDirectoryMaskFromMorphologist,
                        outputDirectoryDiffusionMetricsInWhiteGreyMatter,
                        verbose )

        ##################################################################
        # computing diffusion metrics in FreeSurfer ROIs
        ##################################################################

        outputDirectoryDiffusionMetricsInHippROIs = makeDirectory(
                                        subjectOutputDirectory,
                                        "29-DiffusionMetricsInHippROIs")

        if (taskDescription["DiffusionMetricsInHippROIs"] == 1):

            runDiffusionMetricsInHippROIs(
                            outputDirectoryFreeSurferParcellation,
                            outputDirectoryLocalModelingDTIMultipleShell,
                            outputDirectoryLocalModelingQBIMultipleShell,
                            outputDirectoryMicrostructureField,
                            outputDirectoryMaskFromMorphologist,
                            outputDirectoryDiffusionMetricsInHippROIs,
                            verbose )

        ##################################################################
        # normalization
        ##################################################################

        outputDirectoryNormalization = makeDirectory(
                                                    subjectOutputDirectory,
                                                    "30-Normalization")

        templateDirectory = "/work/templates/mni_icbm152_nlin_asym_09a"

        if (taskDescription["Normalization"] == 1):

            runNormalization( outputDirectoryMaskFromMorphologist,
                                templateDirectory,
                                outputDirectoryNormalization,
                                verbose)

        ##################################################################
        # connectivity matrix
        ##################################################################

        # outputDirectoryConnectivityMatrix = makeDirectory(
        #                                         subjectOutputDirectory,
        #                                         "31-ConnectivityMatrix")

        # if ( session == 'V1' ):

        #   subjectV1ConnectivityMatrixDirectories.append( 
        #                              outputDirectoryConnectivityMatrix )

        # elif ( session == 'V2' ):

        #   subjectV2ConnectivityMatrixDirectories.append( 
        #                              outputDirectoryConnectivityMatrix )

        # else:

        #   subjectV3ConnectivityMatrixDirectories.append( 
        #                              outputDirectoryConnectivityMatrix )

        # if (taskDescription["ConnectivityMatrix"] == 1):

        #     runConnectivityMatrix( 
        #                           outputDirectoryTractographySRD,
        #                           outputDirectoryMaskFromMorphologist,
        #                           outputDirectoryFreeSurferParcellation,
        #                           outputDirectoryNormalization,
        #                           outputDirectoryConnectivityMatrix,
        #                           verbose)

    ############################################################################
    # building roi-to-roi connectivity template 
    ############################################################################

    outputDirectoryFullConnectivityTemplate = makeDirectory( 
                                                 outputDirectory,
                                                 "00-FullConnectivityTemplate" )

    if ( taskDescription["FullConnectivityTemplate"] == 1 ):

      runFullConnectivityTemplate( subjectV1ConnectivityMatrixDirectories,
                                   subjectV2ConnectivityMatrixDirectories,
                                   subjectV3ConnectivityMatrixDirectories,
                                   outputDirectoryFullConnectivityTemplate,
                                   verbose )

    ############################################################################
    # second loop over groups and individuals to compute diffusion metrics in 
    # hippocampi connectivity template
    ############################################################################

    for group in subjects.keys():

        groupOutputDirectory = os.path.join(outputDirectory, str( group ) )

        for subject in subjects[group]:

            subjectOutputDirectoryTemp = os.path.join(groupOutputDirectory,
                                                      str(subject))

            for session in session.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      session)

                if (verbose == True):
                    print("===================================================")
                    print(group + " / " + subject)
                    print("===================================================")

                outputDirectoryLocalModelingDTIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '13-LocalModeling-DTI-Multiple-Shell' )

                outputDirectoryLocalModelingQBIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '17-LocalModeling-QBI-Multiple-Shell' )

                outputDirectoryMicrostructureField = os.path.join( 
                                            subjectOutputDirectory,
                                            '18-NoddiMicrostructureField' )

                outputDirectoryMaskFromMorphologist = os.path.join( 
                                            subjectOutputDirectory,
                                            '07-MaskFromMorphologistPipeline' )

                outputDirectoryNormalization = os.path.join( subjectOutputDirectory,
                                                             '30-Normalization' )

                if ( taskDescription[ "DiffusionMetricsInHippocampiConnectivityTemplate" ] == 1 ):

                  outputDirectoryDiffusionMetricsInHippocampiConnectivityTemplate = makeDirectory(
                                               subjectOutputDirectory,
                                               "32-DiffusionMetricsInHippocampiConnectivityTemplate" )

                  runDiffusionMetricsInHippocampiConnectivityTemplate( 
                                  outputDirectoryFullConnectivityTemplate,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInHippocampiConnectivityTemplate,
                                  verbose )

    ############################################################################
    # second loop over groups and individuals to compute diffusion metrics in 
    # full connectivity template
    ############################################################################

    for group in subjects.keys():

        groupOutputDirectory = os.path.join(outputDirectory, str( group ) )

        for subject in subjects[group]:

            subjectOutputDirectoryTemp = os.path.join(groupOutputDirectory,
                                                      str(subject))

            for session in session.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      session)

                if (verbose == True):
                    print("===================================================")
                    print(group + " / " + subject)
                    print("===================================================")

                outputDirectoryLocalModelingDTIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '13-LocalModeling-DTI-Multiple-Shell' )

                outputDirectoryLocalModelingQBIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '17-LocalModeling-QBI-Multiple-Shell' )

                outputDirectoryMicrostructureField = os.path.join( 
                                            subjectOutputDirectory,
                                            '18-NoddiMicrostructureField' )

                outputDirectoryMaskFromMorphologist = os.path.join( 
                                            subjectOutputDirectory,
                                            '07-MaskFromMorphologistPipeline' )

                outputDirectoryNormalization = os.path.join( subjectOutputDirectory,
                                                             '30-Normalization' )

                outputDirectoryConnectivityMatrix = os.path.join( subjectOutputDirectory,
                                                             '31-ConnectivityMatrix' )

                if ( taskDescription[ "DiffusionMetricsInFullConnectivityTemplate" ] == 1 ):

                  outputDirectoryDiffusionMetricsInFullConnectivityTemplate = makeDirectory(
                                               subjectOutputDirectory,
                                               "33-DiffusionMetricsInFullConnectivityTemplate" )

                  runDiffusionMetricsInFullConnectivityTemplate( 
                                  outputDirectoryFullConnectivityTemplate,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInFullConnectivityTemplate,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInConnectivityMatrix" ] == 1 ):

                  outputDirectoryDiffusionMetricsInConnectivityMatrix = makeDirectory(
                                               subjectOutputDirectory,
                                               "34-DiffusionMetricsInConnectivityMatrix" )

                  runDiffusionMetricsInConnectivityMatrix( 
                                  outputDirectoryConnectivityMatrix,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryDiffusionMetricsInConnectivityMatrix,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInMNISpace" ] == 1 ):

                  outputDirectoryDiffusionMetricsInMNISpace = makeDirectory(
                                               subjectOutputDirectory,
                                               "35-DiffusionMetricsInMNISpace" )

                  runDiffusionMetricsInMNISpace(
                                  templateDirectory, 
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInMNISpace,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInCutExtremitiesConnectivityMatrix" ] == 1 ):

                  outputDirectoryDiffusionMetricsInCutExtremitiesConnectivityMatrix = makeDirectory(
                                               subjectOutputDirectory,
                                               "36-DiffusionMetricsInCutExtremitiesConnectivityMatrix" )

                  runDiffusionMetricsInConnectivityMatrix( 
                                  outputDirectoryConnectivityMatrix,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryDiffusionMetricsInCutExtremitiesConnectivityMatrix,
                                  verbose )

