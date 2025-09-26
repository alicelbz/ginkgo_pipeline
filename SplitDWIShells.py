#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Split a 4D DWI (NIfTI) into separate shells and write matching bval/bvec files.

Defaults:
- expects: <session>/dwi/dwi.nii.gz, dwi.bval, dwi.bvec
- shells: 0, 500, 1000, 2000, 3000
- tolerance: ±50 around each shell value
- outputs in the same dwi/ directory:
    dwi_b0000.nii.gz + .bval + .bvec
    dwi_b0500.nii.gz + .bval + .bvec
    ...

Usage:
  python3 SplitDWIShells.py \
    --session /wynton/scratch/aleberre/projects/Ginkgo_pipeline/data_in/sub-PR07/ses-20250106 \
    [--dwi dwi/dwi.nii.gz] [--bval dwi/dwi.bval] [--bvec dwi/dwi.bvec] \
    [--outdir dwi] [--shells 0 500 1000 2000 3000] [--tol 50] [--verbose]
"""

import os
import sys
import argparse
import numpy as np

try:
    import nibabel as nib
except Exception as e:
    sys.stderr.write(
        "ERROR: nibabel is required. Install it in your environment, e.g.\n"
        "  python3 -m pip install --user nibabel numpy\n"
    )
    raise

def _ensure_file(p):
    if not os.path.isfile(p):
        raise FileNotFoundError(f"Missing file: {p}")
    return p

def run_split(
    session_dir: str,
    dwi_rel: str = "dwi/dwi.nii.gz",
    bval_rel: str = "dwi/dwi.bval",
    bvec_rel: str = "dwi/dwi.bvec",
    outdir_rel: str = "dwi",
    shells = (0, 500, 1000, 2000, 3000),
    tol: float = 50.0,
    verbose: bool = False,
):
    # Resolve paths
    dwi_dir = os.path.join(session_dir, os.path.dirname(dwi_rel))
    out_dir = os.path.join(session_dir, outdir_rel)
    os.makedirs(out_dir, exist_ok=True)

    dwi_path  = _ensure_file(os.path.join(session_dir, dwi_rel))
    bval_path = _ensure_file(os.path.join(session_dir, bval_rel))
    bvec_path = _ensure_file(os.path.join(session_dir, bvec_rel))

    # Load gradients
    bvals = np.loadtxt(bval_path)
    bvecs = np.loadtxt(bvec_path)  # shape (3, N) or (N, 3) depending on writer
    if bvecs.shape[0] != 3 and bvecs.shape[1] == 3:
        bvecs = bvecs.T  # make it (3, N)

    # Load 4D DWI
    img  = nib.load(dwi_path)
    data = img.get_fdata()
    aff  = img.affine
    hdr  = img.header

    if verbose:
        print(f"[SplitDWIShells] DWI:  {dwi_path}")
        print(f"[SplitDWIShells] bval: {bval_path}")
        print(f"[SplitDWIShells] bvec: {bvec_path}")
        print(f"[SplitDWIShells] shape={data.shape}, nvols={data.shape[-1]}")

    # Basic sanity
    nvol = data.shape[-1]
    if not (data.ndim == 4 and nvol == bvals.size and nvol == bvecs.shape[1]):
        raise RuntimeError(
            f"Mismatched volumes: dwi={nvol}, bvals={bvals.size}, bvecs_cols={bvecs.shape[1]}"
        )

    # Split and write
    for b in shells:
        idx = np.where((bvals >= b - tol) & (bvals <= b + tol))[0]
        if idx.size == 0:
            if verbose:
                print(f"[skip] b={b}: no volumes")
            continue

        tag = f"b{b:04d}"
        out_nii  = os.path.join(out_dir, f"dwi_{tag}.nii.gz")
        out_bval = os.path.join(out_dir, f"dwi_{tag}.bval")
        out_bvec = os.path.join(out_dir, f"dwi_{tag}.bvec")

        sub = data[..., idx]
        nib.Nifti1Image(sub, aff, hdr).to_filename(out_nii)
        np.savetxt(out_bval, bvals[idx][None, :], fmt="%.0f")
        np.savetxt(out_bvec, bvecs[:, idx], fmt="%.6f")

        if verbose:
            print(f"[ok]  {out_nii}  vols={idx.size}")
            print(f"      {out_bval}")
            print(f"      {out_bvec}")

def main():
    ap = argparse.ArgumentParser(description="Split 4D DWI into shells and write per-shell bval/bvec.")
    ap.add_argument("--session", required=True,
                    help="Path to the subject session directory (containing dwi/).")
    ap.add_argument("--dwi", default="dwi/dwi.nii.gz", help="Relative path to DWI NIfTI from --session.")
    ap.add_argument("--bval", default="dwi/dwi.bval",   help="Relative path to bval from --session.")
    ap.add_argument("--bvec", default="dwi/dwi.bvec",   help="Relative path to bvec from --session.")
    ap.add_argument("--outdir", default="dwi",          help="Relative output directory under --session.")
    ap.add_argument("--shells", nargs="+", type=float, default=[0, 500, 1000, 2000, 3000],
                    help="Shell centers to extract (e.g. 0 500 1000 2000 3000).")
    ap.add_argument("--tol", type=float, default=50.0,  help="Tolerance around each shell value.")
    ap.add_argument("--verbose", action="store_true",   help="Verbose logging.")
    args = ap.parse_args()

    run_split(
        session_dir=os.path.abspath(args.session),
        dwi_rel=args.dwi,
        bval_rel=args.bval,
        bvec_rel=args.bvec,
        outdir_rel=args.outdir,
        shells=args.shells,
        tol=args.tol,
        verbose=bool(args.verbose),
    )

if __name__ == "__main__":
    main()

