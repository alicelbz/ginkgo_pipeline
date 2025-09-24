#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NIfTI → GIS conversion for the Ginkgo pipeline.

- description: dict mapping keys (e.g., "DWIB0", "T1w") to file paths
  relative to subjectNiftiDirectory (or absolute paths).
- Outputs: <outputDirectory>/<key>.ima (+ .dim) in GIS format.
"""

import os, sys, glob

# Make sure gkg is importable
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
import gkg  # noqa: E402

from CopyFileDirectoryRm import removeMinf


def _resolve_nifti_path(root, spec):
    """Resolve a NIfTI path (absolute, relative, directory, or glob)."""
    cand = spec
    if not os.path.isabs(cand):
        cand = os.path.join(root, spec)

    if os.path.isdir(cand):
        matches = sorted(glob.glob(os.path.join(cand, "*.nii*")))
        if len(matches) != 1:
            raise FileNotFoundError(f"Expected exactly 1 NIfTI in {cand}, found {len(matches)}")
        return matches[0]

    if any(c in cand for c in "*?[]"):
        matches = sorted(glob.glob(cand))
        if len(matches) != 1:
            raise FileNotFoundError(f"Glob '{spec}' resolved to {len(matches)} files")
        return matches[0]

    if os.path.isfile(cand) and cand.endswith((".nii", ".nii.gz")):
        return cand

    raise FileNotFoundError(f"NIfTI not found for spec='{spec}' (resolved {cand})")


def runNifti2GisConversion(subjectNiftiDirectory,
                           description,
                           outputDirectory,
                           verbose):
    """Convert a set of NIfTI inputs to GIS (.ima/.dim)."""
    if verbose:
        print("NIFTI → GIS CONVERSION")
        print("-------------------------------------------------------------")

    os.makedirs(outputDirectory, exist_ok=True)

    for key in sorted(description.keys()):
        fileNameIn = _resolve_nifti_path(subjectNiftiDirectory, description[key])
        fileNameOut = os.path.join(outputDirectory, f"{key}.ima")

        # Core conversion
        gkg.executeCommand({
            "algorithm": "Nifti2GisConverter",
            "parameters": {
                "fileNameIn": str(fileNameIn),
                "fileNameOut": str(fileNameOut),
                "outputFormat": "gis",
                "verbose": verbose,
            },
            "verbose": verbose,
        })
        removeMinf(fileNameOut)

        # Cast / normalize
        gkg.executeCommand({
            "algorithm": "Combiner",
            "parameters": {
                "fileNameIns": str(fileNameOut),
                "fileNameOut": str(fileNameOut),
                "functor1s": "id",
                "functor2s": "id",
                "numerator1s": (1.0, 1.0),
                "denominator1s": (1.0, 1.0),
                "numerator2s": 1.0,
                "denominator2s": 1.0,
                "operators": "*",
                "fileNameMask": "",
                "mode": "gt",
                "threshold1": 0.0,
                "threshold2": 0.0,
                "background": 0.0,
                "outputType": "float",
                "ascii": False,
                "format": "gis",
                "verbose": verbose,
            },
            "verbose": verbose,
        })
        removeMinf(fileNameOut)

    if verbose:
        print("-------------------------------------------------------------")
