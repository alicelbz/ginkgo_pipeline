#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Field map–based susceptibility distortion correction for DWI (FSL).

Expected BIDS-like layout under a session:
  session_dir/
    dwi/
      dwi.nii.gz
      dwi.bval
      dwi.bvec
      dwi.json          # contains PhaseEncodingDirection, EffectiveEchoSpacing or TotalReadoutTime
    fmap/
      sub-*_phasediff.nii.gz + sub-*_phasediff.json + magnitude1.nii.gz [preferred]
      OR
      sub-*_phase1.nii.gz + sub-*_phase1.json + sub-*_phase2.nii.gz + sub-*_phase2.json (+ magnitudes)

Output:
  output_dir/
    fmap_rads.nii.gz        # fieldmap in rad/s (FSL format)
    dwi_fmapcorr.nii.gz     # distortion-corrected 4D DWI
"""

import os, json, glob, shutil, subprocess

def _run(cmd, verbose=True):
    if verbose:
        print(cmd, flush=True)
    return subprocess.call(cmd, shell=True)

def _load_json(p):
    with open(p, "r") as f:
        return json.load(f)

def _exists(p): return p and os.path.isfile(p)

def _bids_find_fmap(session_dir):
    """Return a dict describing the fieldmap set we can use."""
    fmap_dir = os.path.join(session_dir, "fmap")

    # Prefer phasediff
    phasediff = sorted(glob.glob(os.path.join(fmap_dir, "*phasediff.nii*")))
    if phasediff:
        phnii = phasediff[0]
        phjson = os.path.splitext(phnii)[0] + ".json"
        # pick a magnitude
        mags = sorted(glob.glob(os.path.join(fmap_dir, "*magnitude1.nii*"))) or \
               sorted(glob.glob(os.path.join(fmap_dir, "*magnitude.nii*")))
        mag = mags[0] if mags else None
        return {"mode": "phasediff", "phase": phnii, "phase_json": phjson, "mag": mag}

    # Else look for phase1/phase2
    phase1 = sorted(glob.glob(os.path.join(fmap_dir, "*phase1.nii*")))
    phase2 = sorted(glob.glob(os.path.join(fmap_dir, "*phase2.nii*")))
    if phase1 and phase2:
        p1 = phase1[0]; p2 = phase2[0]
        p1j = os.path.splitext(p1)[0] + ".json"
        p2j = os.path.splitext(p2)[0] + ".json"
        mags = sorted(glob.glob(os.path.join(fmap_dir, "*magnitude1.nii*"))) or \
               sorted(glob.glob(os.path.join(fmap_dir, "*magnitude.nii*")))
        mag = mags[0] if mags else None
        return {"mode": "phase12", "phase1": p1, "phase1_json": p1j, "phase2": p2, "phase2_json": p2j, "mag": mag}

    return None

def _phase_dir_to_fugue_unwarpdir(phase_dir):
    """
    Map BIDS PhaseEncodingDirection (i/j/k with optional -)
    to FUGUE's --unwarpdir (x/y/z with +/-).
    """
    if not phase_dir:
        return None
    axis = phase_dir[0]
    sign = "-" if len(phase_dir) > 1 and phase_dir[1] == "-" else ""
    mapping = {"i": "x", "j": "y", "k": "z"}
    if axis not in mapping:
        return None
    return mapping[axis] + sign

def _read_dwi_meta(session_dir):
    dwi_json = os.path.join(session_dir, "dwi", "dwi.json")
    meta = _load_json(dwi_json) if os.path.isfile(dwi_json) else {}
    ped = meta.get("PhaseEncodingDirection") or meta.get("PhaseEncodingDirectionDICOM")
    ees = meta.get("EffectiveEchoSpacing", None)
    trt = meta.get("TotalReadoutTime", None)
    return ped, ees, trt

def _delta_te_from_jsons(ph_json=None, p1_json=None, p2_json=None):
    """
    Return ΔTE (seconds) from fieldmap JSON(s).
    - For phasediff.json: EchoTime1 & EchoTime2.
    - For phase1/phase2: read EchoTime from each.
    """
    if ph_json and os.path.isfile(ph_json):
        j = _load_json(ph_json)
        et1 = j.get("EchoTime1"); et2 = j.get("EchoTime2")
        if et1 is not None and et2 is not None:
            return float(et2) - float(et1)

    if p1_json and p2_json and os.path.isfile(p1_json) and os.path.isfile(p2_json):
        j1 = _load_json(p1_json)
        j2 = _load_json(p2_json)
        et1 = j1.get("EchoTime"); et2 = j2.get("EchoTime")
        if et1 is not None and et2 is not None:
            return float(et2) - float(et1)

    return None

def runFieldmapCorrection(
    subjectSessionDir,
    outputDirectory,
    verbose=True,
    dwi_rel="dwi/dwi.nii.gz",
    require_fsl=True,
    manufacturer="generic"   # "generic" for GE/Philips; "SIEMENS" only for Siemens phasediff
):
    """
    Perform field map–based EPI distortion correction on 4D DWI.

    subjectSessionDir : path to .../sub-XXX/ses-YYY
    outputDirectory   : where fmap_rads.nii.gz and dwi_fmapcorr.nii.gz are written
    dwi_rel           : relative path to the DWI 4D NIfTI within session (default 'dwi/dwi.nii.gz')
    require_fsl       : if True, fail fast if FSL tools are not available
    manufacturer      : "generic" (default) for GE/Philips; use "SIEMENS" for Siemens phasediff
    """
    if verbose:
        print("FIELDMAP-BASED DISTORTION CORRECTION (FSL)")
        print("-------------------------------------------------------------")
        print("session:", subjectSessionDir)

    os.makedirs(outputDirectory, exist_ok=True)

    # Check DWI
    dwi4d = os.path.join(subjectSessionDir, dwi_rel)
    if not os.path.isfile(dwi4d):
        print(f"[WARN] DWI not found: {dwi4d} — skipping fieldmap correction.")
        return

    # Check FSL tools
    needed = ["fsl_prepare_fieldmap", "fugue", "fslmaths"]
    have_all = all(shutil.which(x) for x in needed)
    if require_fsl and not have_all:
        print("[ERROR] Required FSL tools not found in PATH:", ", ".join(needed))
        print("        Load FSL on Wynton (e.g., 'module load fsl') and retry.")
        return

    # DWI meta: unwarp direction and dwell time
    ped, ees, trt = _read_dwi_meta(subjectSessionDir)
    unwarpdir = _phase_dir_to_fugue_unwarpdir(ped)
    if not unwarpdir:
        print(f"[WARN] Could not determine unwarpdir from PhaseEncodingDirection={ped}; defaulting to y-")
        unwarpdir = "y-"

    dwell = None
    if ees is not None:
        dwell = float(ees)
    elif trt is not None:
        # FUGUE wants dwell time per PE line; TotalReadoutTime is (Npe-1)*ees.
        # We don't know Npe here, so we prefer EffectiveEchoSpacing whenever possible.
        print("[WARN] EffectiveEchoSpacing missing; you provided TotalReadoutTime, but FUGUE needs dwell time.")
        print("      If results look off, add 'EffectiveEchoSpacing' to dwi.json.")
        # As a last resort (not exact), pass TRT — FUGUE will interpret it as dwell; not ideal:
        dwell = float(trt)

    if dwell is None:
        print("[ERROR] Neither EffectiveEchoSpacing nor TotalReadoutTime present; cannot run FUGUE safely.")
        return

    # Find fieldmap set
    fmap = _bids_find_fmap(subjectSessionDir)
    if fmap is None:
        print(f"[WARN] No BIDS fieldmap found under {os.path.join(subjectSessionDir,'fmap')}; skipping.")
        return

    # Build/prepare a phase difference image and delta TE
    fmap_rads = os.path.join(outputDirectory, "fmap_rads.nii.gz")

    if fmap["mode"] == "phasediff":
        dte = _delta_te_from_jsons(ph_json=fmap["phase_json"])
        if dte is None:
            print(f"[ERROR] EchoTime1/EchoTime2 not found in {fmap['phase_json']}; cannot continue.")
            return
        if not _exists(fmap["mag"]):
            print("[WARN] magnitude image not found; proceeding without magnitude brain mask.")
            mag = fmap["phase"]  # will still run, but less robust
        else:
            mag = fmap["mag"]

        # phase is already phase-difference (radians). Prepare fieldmap (rad/s).
        cmd_prep = f"fsl_prepare_fieldmap {manufacturer} {fmap['phase']} {mag} {fmap_rads} {dte}"
        if _run(cmd_prep, verbose) != 0:
            print("[ERROR] fsl_prepare_fieldmap failed.")
            return

    else:  # phase1/phase2
        dte = _delta_te_from_jsons(p1_json=fmap["phase1_json"], p2_json=fmap["phase2_json"])
        if dte is None:
            print(f"[ERROR] EchoTime missing in {fmap['phase1_json']} or {fmap['phase2_json']}; cannot continue.")
            return

        phasediff = os.path.join(outputDirectory, "phasediff.nii.gz")
        cmd_diff = f"fslmaths {fmap['phase2']} -sub {fmap['phase1']} -odt float {phasediff}"
        if _run(cmd_diff, verbose) != 0:
            print("[ERROR] fslmaths phase2 - phase1 failed.")
            return

        mag = fmap.get("mag") or fmap["phase1"]  # fall back if magnitude missing
        cmd_prep = f"fsl_prepare_fieldmap {manufacturer} {phasediff} {mag} {fmap_rads} {dte}"
        if _run(cmd_prep, verbose) != 0:
            print("[ERROR] fsl_prepare_fieldmap failed.")
            return

    # Apply the fieldmap to unwarp DWI
    dwi_corr = os.path.join(outputDirectory, "dwi_fmapcorr.nii.gz")
    cmd_fugue = (
        f"fugue -i {dwi4d} "
        f"--dwell={dwell} "
        f"--loadfmap={fmap_rads} "
        f"--unwarpdir={unwarpdir} "
        f"-u {dwi_corr}"
    )
    if _run(cmd_fugue, verbose) != 0:
        print("[ERROR] fugue failed.")
        return

    if verbose:
        print(f"[OK] Wrote: {dwi_corr}")
        print("-------------------------------------------------------------")
