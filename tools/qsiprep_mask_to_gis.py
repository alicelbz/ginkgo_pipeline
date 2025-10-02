#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import argparse
import sys

# GKG python (inside the container)
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import CommandFactory

def removeMinf(path_without_minf_ext):
    """
    Minimal local reimplementation: remove '<path>.minf' if present.
    The original CopyFileDirectoryRm.removeMinf() isn't available here.
    """
    cand = path_without_minf_ext + ".minf"
    try:
        if os.path.isfile(cand):
            os.remove(cand)
    except Exception:
        pass

def convert_nifti_to_gis(nifti_in, ima_out, verbose=False):
    if verbose:
        print("algorithm : Nifti2GisConverter\n")
        print(f"  fileNameIn -> {nifti_in}")
        print(f"  fileNameOut -> {ima_out}")
        print("  outputFormat -> gis")
        print(f"  ascii -> 0\n  verbose -> {1 if verbose else 0}\n")
        print("running Nifti2GisConverter ...\n")

    CommandFactory().executeCommand({
        "algorithm": "Nifti2GisConverter",
        "parameters": {
            "fileNameIn":  str(nifti_in),
            "fileNameOut": str(ima_out),
            "outputFormat":"gis",
            "ascii": False,
            "verbose": verbose
        },
        "verbose": verbose
    })
    # Ensure no stale .minf interferes with later steps
    removeMinf(ima_out)

def main():
    ap = argparse.ArgumentParser(description="Convert QSIPrep mask (+optional T1w) to GIS for Ginkgo.")
    ap.add_argument("--qsiprep_mask", required=True, help="Path to QSIPrep brain mask (NIfTI).")
    ap.add_argument("--qsiprep_t1", default="", help="Optional QSIPrep T1w preproc (NIfTI).")
    ap.add_argument("--outdir", required=True, help="Output directory (e.g., 08-MaskFromMorphologistPipeline).")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    mask_in = args.qsiprep_mask
    t1_in   = args.qsiprep_t1.strip()
    outdir  = args.outdir
    verbose = args.verbose

    os.makedirs(outdir, exist_ok=True)

    if verbose:
        print(f"[qsiprep_mask_to_gis] mask: {mask_in}")
        if t1_in:
            print(f"[qsiprep_mask_to_gis]  T1w: {t1_in}")
        print(f"[qsiprep_mask_to_gis] outdir: {outdir}")

    # Convert mask -> GIS
    mask_ima = os.path.join(outdir, "mask.ima")
    convert_nifti_to_gis(mask_in, mask_ima, verbose=verbose)

    # Optionally convert T1w -> GIS (useful for later steps)
    if t1_in:
        t1_ima = os.path.join(outdir, "T1w.ima")
        convert_nifti_to_gis(t1_in, t1_ima, verbose=verbose)

    if verbose:
        print("[qsiprep_mask_to_gis] done.")

if __name__ == "__main__":
    main()
