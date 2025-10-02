#!/usr/bin/env python3
import os, sys, json
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import *
from CopyFileDirectoryRm import *

import argparse
ap = argparse.ArgumentParser()
ap.add_argument("--qsiprep_mask", required=True)   # e.g. ..._space-T1w_desc-brain_mask.nii.gz
ap.add_argument("--outdir", required=True)         # e.g. /results/sub-XX/ses-YY/08-MaskFromMorphologistPipeline
ap.add_argument("--verbose", action="store_true")
args = ap.parse_args()

os.makedirs(args.outdir, exist_ok=True)
mask_ima = os.path.join(args.outdir, "mask.ima")

# 1) Convert NIfTI brain mask -> GIS mask.ima
CommandFactory().executeCommand({
  "algorithm": "Nifti2GisConverter",
  "parameters": {
    "fileNameIn":  str(args.qsiprep_mask),
    "fileNameOut": str(mask_ima),
    "outputFormat":"gis",
    "ascii": False,
    "verbose": args.verbose
  },
  "verbose": args.verbose
})
removeMinf(mask_ima)

# 2) Identity transforms (since DWI is already in T1w/ACPC space)
def write_trm(path):
  with open(path, "w") as f:
    # 4x4 identity (AIMS .trm)
    f.write(" ".join(map(str, [
      1,0,0,0,
      0,1,0,0,
      0,0,1,0,
      0,0,0,1
    ])) + "\n")

write_trm(os.path.join(args.outdir, "dw-to-t1.trm"))
write_trm(os.path.join(args.outdir, "t1-to-dw.trm"))

if args.verbose:
  print("[QSIPrep→GIS] Wrote:", mask_ima)
  print("[QSIPrep→GIS] Identity transforms: dw-to-t1.trm, t1-to-dw.trm")
