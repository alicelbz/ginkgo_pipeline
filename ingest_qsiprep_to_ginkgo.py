#!/usr/bin/env python3
import os, sys, glob, argparse, shutil

def pick_one(pattern, required=True, label="file"):
    matches = sorted(glob.glob(pattern))
    if matches:
        return matches[0]
    if required:
        print(f"[ERROR] Missing {label}: {pattern}")
        base = os.path.dirname(pattern)
        print(f"[DEBUG] Exists? {base} -> {os.path.isdir(base)}")
        if os.path.isdir(base):
            ls = sorted(os.listdir(base))
            print("[DEBUG] First 30 entries in dir:")
            for i, f in enumerate(ls[:30], 1):
                print(f"  {i:02d}. {f}")
        raise FileNotFoundError(f"Missing {label}: {pattern}")
    return None

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p

def cp(src, dst):
    ensure_dir(os.path.dirname(dst))
    shutil.copy2(src, dst)
    print(f"[COPY] {src} -> {dst}")

def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="Ingest QSIPrep derivatives (on Wynton) into Ginkgo data_in skeleton."
    )
    ap.add_argument(
        "--qsiprep_root",
        default="/wynton/data/BIDS/derivatives/qsiprep",   # <-- chemin par défaut correct
        help="Wynton path to QSIPrep derivatives root "
             "(default: /wynton/data/BIDS/derivatives/qsiprep)"
    )
    ap.add_argument("--subject", required=True, help="e.g. sub-PR07")
    ap.add_argument("--session", required=True, help="e.g. ses-20241220")
    ap.add_argument(
        "--out_root",
        required=True,
        help="Ginkgo data_in root (e.g. /wynton/scratch/.../Ginkgo_pipeline/data_in)"
    )
    ap.add_argument("--dryrun", action="store_true")
    args = ap.parse_args()

    sub = args.subject
    ses = args.session

    # QSIPrep expected structure on WYNTON
    qp_sub_ses = os.path.join(args.qsiprep_root, sub, ses)
    qp_dwi = os.path.join(qp_sub_ses, "dwi")
    qp_anat = os.path.join(qp_sub_ses, "anat")

    if not os.path.isdir(qp_sub_ses):
        print(f"[ERROR] QSIPrep subject/session not found on Wynton: {qp_sub_ses}")
        sys.exit(2)

    # Patterns (cluster paths only, no macOS prefixes)
    pat_dwi_nii  = os.path.join(qp_dwi, f"{sub}_{ses}_*space-ACPC_desc-preproc_dwi.nii.gz")
    pat_dwi_bval = os.path.join(qp_dwi, f"{sub}_{ses}_*space-ACPC_desc-preproc_dwi.bval")
    pat_dwi_bvec = os.path.join(qp_dwi, f"{sub}_{ses}_*space-ACPC_desc-preproc_dwi.bvec")
    pat_dwi_json = os.path.join(qp_dwi, f"{sub}_{ses}_*space-ACPC_desc-preproc_dwi.json")

    pat_t1_nii   = os.path.join(qp_anat, f"{sub}_{ses}_space-ACPC_desc-preproc_T1w.nii.gz")
    pat_mask_nii = os.path.join(qp_anat, f"{sub}_{ses}_space-ACPC_desc-brain_mask.nii.gz")

    # Resolve actual files
    dwi_nii  = pick_one(pat_dwi_nii,  True,  "DWI NIfTI")
    dwi_bval = pick_one(pat_dwi_bval, True,  "DWI bval")
    dwi_bvec = pick_one(pat_dwi_bvec, True,  "DWI bvec")
    dwi_json = pick_one(pat_dwi_json, False, "DWI JSON")  # optional

    t1_nii   = pick_one(pat_t1_nii,   True,  "T1w NIfTI")
    mask_nii = pick_one(pat_mask_nii, True,  "T1 brain mask")

    # Ginkgo target layout
    out_session = os.path.join(args.out_root, sub, ses)
    out_dwi = ensure_dir(os.path.join(out_session, "dwi"))
    out_anat = ensure_dir(os.path.join(out_session, "anat"))

    # DWI → canonical Ginkgo names
    dwi_dst_nii  = os.path.join(out_dwi,  "dwi.nii.gz")
    dwi_dst_bval = os.path.join(out_dwi,  "dwi.bval")
    dwi_dst_bvec = os.path.join(out_dwi,  "dwi.bvec")
    dwi_dst_json = os.path.join(out_dwi,  "dwi.json")

    # T1 + mask
    t1_dst_nii   = os.path.join(out_anat, "T1w.nii.gz")
    mask_dst_nii = os.path.join(out_anat, "T1w_brain_mask.nii.gz")

    print("\n[PLAN] Copying files into Ginkgo layout:")
    print(f"  DWI  : {dwi_nii}  -> {dwi_dst_nii}")
    print(f"  bval : {dwi_bval} -> {dwi_dst_bval}")
    print(f"  bvec : {dwi_bvec} -> {dwi_dst_bvec}")
    if dwi_json:
        print(f"  json : {dwi_json} -> {dwi_dst_json}")
    else:
        print("  json : (none found; continuing)")

    print(f"  T1w  : {t1_nii}   -> {t1_dst_nii}")
    print(f"  mask : {mask_nii} -> {mask_dst_nii}\n")

    if args.dryrun:
        print("[DRYRUN] No files copied.")
        return

    # Do copies
    cp(dwi_nii,  dwi_dst_nii)
    cp(dwi_bval, dwi_dst_bval)
    cp(dwi_bvec, dwi_dst_bvec)
    if dwi_json:
        cp(dwi_json, dwi_dst_json)

    cp(t1_nii,   t1_dst_nii)
    cp(mask_nii, mask_dst_nii)

    print("\n[OK] QSIPrep ingestion complete.")

if __name__ == "__main__":
    main()
