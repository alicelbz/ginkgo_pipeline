#!/usr/bin/env python3
import os, sys, argparse, subprocess

# Ensure Ginkgo libs are on path (inside container this is /usr/share/gkg/python)
sys.path.insert(0, "/usr/share/gkg/python")
try:
    from core.command.CommandFactory import CommandFactory
except Exception as e:
    print("[ERROR] Cannot import CommandFactory from Ginkgo (/usr/share/gkg/python).", file=sys.stderr)
    raise

# Optional project-local helper; if missing, provide a fallback.
try:
    from CopyFileDirectoryRm import removeMinf  # project helper
except Exception:
    def removeMinf(fileNameIma: str):
        """
        Minimal fallback: if a .minf (or .dim.minf) next to the .ima exists, delete it.
        This mimics the behavior used elsewhere in the pipeline.
        """
        base, ext = os.path.splitext(fileNameIma)
        # .ima -> .minf
        cand1 = base + ".minf" if ext.lower()==".ima" else fileNameIma + ".minf"
        # .dim.minf (sometimes BrainVISA writes both)
        cand2 = base + ".dim.minf"
        for p in (cand1, cand2):
            try:
                if os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)
    return d

def write_identity_trm(path):
    # 4x4 identity in .trm ASCII format
    with open(path, "w") as f:
        f.write(
            "%% transformation matrix\n"
            "1 0 0 0\n"
            "0 1 0 0\n"
            "0 0 1 0\n"
            "0 0 0 1\n"
        )

def main():
    ap = argparse.ArgumentParser(
        description="Convert QSIPrep outputs (mask/T1w) to GIS and write identity transforms."
    )
    ap.add_argument("--qsiprep_mask", required=True,
                    help="QSIPrep brain mask NIfTI (space-* desc-brain_mask.nii.gz)")
    ap.add_argument("--qsiprep_t1", default="",
                    help="(optional) QSIPrep T1w NIfTI (space-* desc-preproc_T1w.nii.gz) to convert to GIS")
    ap.add_argument("--outdir", required=True, help="Output directory (08-MaskFromMorphologistPipeline)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    mask_nii = args.qsiprep_mask
    t1_nii   = args.qsiprep_t1
    outdir   = ensure_dir(args.outdir)

    if args.verbose:
        print("[qsiprep_mask_to_gis] mask:", mask_nii)
        if t1_nii:
            print("[qsiprep_mask_to_gis]  T1w:", t1_nii)
        print("[qsiprep_mask_to_gis] outdir:", outdir)

    # Convert mask → GIS
    mask_ima = os.path.join(outdir, "mask.ima")
    CommandFactory().executeCommand({
        "algorithm": "Nifti2GisConverter",
        "parameters": {
            "fileNameIn":  str(mask_nii),
            "fileNameOut": str(mask_ima),
            "outputFormat": "gis",
            "ascii": False,
            "verbose": args.verbose
        },
        "verbose": args.verbose
    })
    removeMinf(mask_ima)

    # Optionally convert T1w → GIS for completeness (some steps expect it)
    if t1_nii:
        t1_ima = os.path.join(outdir, "T1w.ima")
        CommandFactory().executeCommand({
            "algorithm": "Nifti2GisConverter",
            "parameters": {
                "fileNameIn":  str(t1_nii),
                "fileNameOut": str(t1_ima),
                "outputFormat": "gis",
                "ascii": False,
                "verbose": args.verbose
            },
            "verbose": args.verbose
        })
        removeMinf(t1_ima)

    # Write identity transforms expected by later steps
    write_identity_trm(os.path.join(outdir, "dw-to-t1.trm"))
    write_identity_trm(os.path.join(outdir, "t1-to-dw.trm"))
    write_identity_trm(os.path.join(outdir, "dw-to-talairach.trm"))

    if args.verbose:
        print("[qsiprep_mask_to_gis] done.")

if __name__ == "__main__":
    main()
