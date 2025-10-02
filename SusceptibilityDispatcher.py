#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil

# Ginkgo env (dans le conteneur)
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))

# Optional imports (present in the image)
TOPUP_OK = False
FIELDMAP_OK = False
try:
    from SusceptibilityArtifactFromTopUpCorrection import runTopUpCorrection
    TOPUP_OK = True
except Exception:
    pass

try:
    from FieldmapCorrection import runFieldmapCorrection
    FIELDMAP_OK = True
except Exception:
    pass


def _exists(p): return p and os.path.isfile(p)

def _load_json(p):
    with open(p, "r") as f:
        return json.load(f)

def _iter_subjects(subjects_json):
    """
    Accepte :
      A) {"patients":{"sub-PR08":["ses-20250723"], ...}}
      B) {"subjects":[{"id":"sub-PR08","sessions":["ses-20250723"]}, ...]}
    """
    if isinstance(subjects_json, dict) and "patients" in subjects_json:
        for sid, sessions in subjects_json["patients"].items():
            for ses in sessions:
                yield sid, ses
        return
    if isinstance(subjects_json, dict) and "subjects" in subjects_json:
        for rec in subjects_json["subjects"]:
            sid = rec.get("id")
            for ses in rec.get("sessions", []):
                yield sid, ses

def _has_topup_pair(session_dir):
    """AP/PA b0 en fmap/ (AP.nii.gz, PA.nii.gz + json)"""
    fmap = os.path.join(session_dir, "fmap")
    ap_nii = os.path.join(fmap, "AP.nii.gz")
    pa_nii = os.path.join(fmap, "PA.nii.gz")
    ap_js  = os.path.join(fmap, "AP.json")
    pa_js  = os.path.join(fmap, "PA.json")
    return _exists(ap_nii) and _exists(pa_nii) and _exists(ap_js) and _exists(pa_js)

def _has_fieldmap(session_dir):
    """phasediff + magnitude1 + magnitude2 (noms BIDS classiques)"""
    fmap = os.path.join(session_dir, "fmap")
    if not os.path.isdir(fmap):
        return (False, None, None, None)
    candidates = []
    for root, _, files in os.walk(fmap):
        for f in files:
            candidates.append(os.path.join(root, f))
    phase = [p for p in candidates if "phasediff" in os.path.basename(p) and p.endswith((".nii", ".nii.gz"))]
    mag1  = [p for p in candidates if "magnitude1" in os.path.basename(p) and p.endswith((".nii", ".nii.gz"))]
    mag2  = [p for p in candidates if "magnitude2" in os.path.basename(p) and p.endswith((".nii", ".nii.gz"))]
    return (len(phase) > 0 and len(mag1) > 0 and len(mag2) > 0,
            phase[0] if phase else None,
            mag1[0] if mag1 else None,
            mag2[0] if mag2 else None)

def _copy_gradients(src_dwi_dir, dst_dir, base_out):
    """Copies dwi.bval/.bvec from src_dwi_dir to dst_dir/base_out.{bval,bvec}"""
    bval_in = os.path.join(src_dwi_dir, "dwi.bval")
    bvec_in = os.path.join(src_dwi_dir, "dwi.bvec")
    if _exists(bval_in):
        shutil.copy2(bval_in, os.path.join(dst_dir, f"{base_out}.bval"))
    if _exists(bvec_in):
        shutil.copy2(bvec_in, os.path.join(dst_dir, f"{base_out}.bvec"))

def main():
    import argparse
    ap = argparse.ArgumentParser(description="Dispatch susceptibility correction: TopUp (AP/PA) or Fieldmap.")
    ap.add_argument("--input_root",  required=True, help="Racine des données d'entrée (ex: /data_in)")
    ap.add_argument("--output_root", required=True, help="Racine des résultats (ex: /results)")
    ap.add_argument("--subjects_json", required=True, help="subjects.json")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    with open(args.subjects_json, "r") as f:
        subjects = json.load(f)

    for sid, ses in _iter_subjects(subjects):
        session_dir = os.path.join(args.input_root, sid, ses)          # .../data_in/sub-XX/ses-YY
        dwi_dir     = os.path.join(session_dir, "dwi")
        dwi_4d      = os.path.join(dwi_dir, "dwi.nii.gz")
        bval_4d     = os.path.join(dwi_dir, "dwi.bval")
        bvec_4d     = os.path.join(dwi_dir, "dwi.bvec")

        if not _exists(dwi_4d):
            print(f"[WARN] DWI manquant pour {sid}/{ses} : {dwi_4d} — skip.")
            continue

        # Output dir for this step (preproc/distortion correction normalized here)
        dir01_dc = os.path.join(args.output_root, sid, ses, "01-DistortionCorrection")
        os.makedirs(dir01_dc, exist_ok=True)

        print("="*60)
        print(f"[Dispatcher] {sid} / {ses}")
        print("="*60)

        # Default normalized outputs expected by the rest of the pipeline
        dwi_dc  = os.path.join(dir01_dc, "dwi_dc.nii.gz")
        bval_dc = os.path.join(dir01_dc, "dwi_dc.bval")
        bvec_dc = os.path.join(dir01_dc, "dwi_dc.bvec")

        # 1) Try TopUp if AP/PA are available
        if _has_topup_pair(session_dir):
            if not TOPUP_OK:
                print("[ERROR] TopUp module introuvable (SusceptibilityArtifactFromTopUpCorrection.py).")
                sys.exit(2)

            if args.verbose:
                print("[Dispatcher] TopUp: AP/PA détectés → runTopUpCorrection")

            runTopUpCorrection(
                subjectDirectoryNiftiConversion=session_dir,
                outputDirectory=dir01_dc,
                verbose=args.verbose
            )

            topup_out = os.path.join(dir01_dc, "dwi_topup.nii.gz")
            if _exists(topup_out):
                shutil.copy2(topup_out, dwi_dc)
            else:
                raise RuntimeError(f"TopUp n'a pas produit {topup_out}")

            # propagate input gradients unchanged at this stage
            shutil.copy2(bval_4d, bval_dc)
            shutil.copy2(bvec_4d, bvec_dc)
            continue  # done for this subject/session

        # 2) Else, try classic fieldmap
        has_fmap, phasediff, mag1, mag2 = _has_fieldmap(session_dir)
        if has_fmap:
            if not FIELDMAP_OK:
                print("[ERROR] FieldmapCorrection introuvable. Place FieldmapCorrection.py dans le PYTHONPATH.")
                sys.exit(3)

            if args.verbose:
                print("[Dispatcher] Fieldmap: phasediff/magnitude détectés → runFieldmapCorrection")

            # Standardize call: this function should write dwi_dc.nii.gz (or something we map to it)
            # If your runFieldmapCorrection has a different signature, adapt here:
            try:
                runFieldmapCorrection(
                    subjectSessionDir=session_dir,
                    dwi=dwi_4d, bval=bval_4d, bvec=bvec_4d,
                    outDir=dir01_dc,
                    verbose=args.verbose
                )
            except TypeError:
                # Fallback for older API variants
                runFieldmapCorrection(session_dir, dir01_dc, args.verbose)

            # If the script used a different basename, normalize to dwi_dc.*
            # Common alt name:
            fmap_nii = os.path.join(dir01_dc, "dwi_fieldmap.nii.gz")
            if _exists(fmap_nii) and not _exists(dwi_dc):
                shutil.copy2(fmap_nii, dwi_dc)
            elif not _exists(dwi_dc):
                raise RuntimeError("Fieldmap: aucun des fichiers de sortie attendus n'a été trouvé (dwi_dc.nii.gz/dwi_fieldmap.nii.gz)")

            if not _exists(bval_dc): shutil.copy2(bval_4d, bval_dc)
            if not _exists(bvec_dc): shutil.copy2(bvec_4d, bvec_dc)
            continue  # done for this subject/session

        # 3) Neither AP/PA nor fieldmap → passthrough (not recommended)
        print("[WARN] Ni AP/PA ni fieldmap trouvés. Aucune correction de susceptibilité appliquée.")
        shutil.copy2(dwi_4d,  dwi_dc)
        shutil.copy2(bval_4d, bval_dc)
        shutil.copy2(bvec_4d, bvec_dc)

    print("[Dispatcher] Terminé.")


if __name__ == "__main__":
    main()
