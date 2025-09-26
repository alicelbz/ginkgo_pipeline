#!/usr/bin/env python3
import os, numpy as np

def runSplitDWIShells(subjectSessionDir, outDir, verbose=True):
    """
    Split a 4D DWI into per-shell volumes and write matching bval/bvec files.

    Expects:
      subjectSessionDir/
        └── dwi/
            ├── dwi.nii.gz
            ├── dwi.bval
            └── dwi.bvec

    Creates in outDir:
      dwi_b0000.nii.gz, dwi_b0500.nii.gz, dwi_b1000.nii.gz, ...
      with matching dwi_bXXXX.bval / dwi_bXXXX.bvec
    """
    dwi_dir = os.path.join(subjectSessionDir, "dwi")
    nii_path  = os.path.join(dwi_dir, "dwi.nii.gz")
    bval_path = os.path.join(dwi_dir, "dwi.bval")
    bvec_path = os.path.join(dwi_dir, "dwi.bvec")

    if verbose:
        print("\n[Step 00] SPLIT DWI INTO SHELLS")
        print("--------------------------------------")
        print(f"Input DWI : {nii_path}")
        print(f"Input bval: {bval_path}")
        print(f"Input bvec: {bvec_path}")

    if not (os.path.isfile(nii_path) and os.path.isfile(bval_path) and os.path.isfile(bvec_path)):
        print(f"[WARN] Missing DWI/bval/bvec in {dwi_dir}; skipping shell split.")
        return

    os.makedirs(outDir, exist_ok=True)

    try:
        import nibabel as nib
    except ImportError:
        print("[WARN] nibabel not installed; skipping shell split.")
        return

    bvals = np.loadtxt(bval_path)
    bvecs = np.loadtxt(bvec_path)
    img   = nib.load(nii_path)
    data  = img.get_fdata()
    aff   = img.affine
    hdr   = img.header

    if data.ndim != 4:
        print("[WARN] Input DWI is not 4D; skipping.")
        return

    shells = [0, 500, 1000, 2000, 3000]
    tol = 50

    def write_shell(tag, idx):
        if idx.size == 0:
            return
        sub = data[..., idx]
        nib.Nifti1Image(sub, aff, hdr).to_filename(os.path.join(outDir, f"dwi_{tag}.nii.gz"))
        np.savetxt(os.path.join(outDir, f"dwi_{tag}.bval"), bvals[idx][None,:], fmt="%.0f")
        np.savetxt(os.path.join(outDir, f"dwi_{tag}.bvec"), bvecs[:,idx], fmt="%.6f")
        if verbose:
            print(f"  -> wrote dwi_{tag}.nii.gz (nvols={idx.size})")

    for b in shells:
        idx = np.where((bvals >= b - tol) & (bvals <= b + tol))[0]
        write_shell(f"b{b:04d}", idx)

    if verbose:
        print("--------------------------------------")
