#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, shutil, subprocess

# GKG for executeCommand only (we won't import gkg.core to read headers)
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
import gkg  # noqa: E402

from CopyFileDirectoryRm import *  # noqa: F401,F403


# -----------------------------
# helpers
# -----------------------------
def _read_minf_attrs(ima_path):
    """
    Read GIS attributes from whichever sidecar exists:
      <base>.dim.minf (PRIMARY), <base>.ima.minf, or <base>.minf
    Returns (attrs_dict, which_file) or ({}, None) on failure.
    """
    base, _ = os.path.splitext(ima_path)
    for cand in (base + ".dim.minf", base + ".ima.minf", base + ".minf"):
        if os.path.isfile(cand):
            ns = {}
            try:
                with open(cand, "r") as f:
                    code = f.read()
                exec(code, ns)
                attrs = ns.get("attributes", {})
                return attrs, cand
            except Exception:
                pass
    return {}, None


def _has_gradients(attrs):
    return (
        isinstance(attrs, dict)
        and "diffusion_gradient_orientations" in attrs
        and isinstance(attrs["diffusion_gradient_orientations"], (list, tuple))
        and len(attrs["diffusion_gradient_orientations"]) > 0
    )


def _inject_gradients_with_tool(ima_path, bval_path, bvec_path, shell_b=None, verbose=False):
    """
    Use /work/tools/add_gradients_to_ima.py to write .dim.minf (and friends).
    """
    cmd = ["python3", "/work/tools/add_gradients_to_ima.py", "--ima", ima_path, "--bvec", bvec_path]
    if bval_path and os.path.isfile(bval_path):
        cmd += ["--bval", bval_path]
    elif shell_b is not None:
        cmd += ["--shell_bvalue", str(shell_b)]
    if verbose:
        print("[inject]", " ".join(cmd))
    subprocess.run(cmd, check=True)


# -----------------------------
# main API (called by RunPipeline.py)
# -----------------------------
def runLocalModelingDTI(fileNameDw,
                        subjectDirectoryEddyCurrentAndMotionCorrection,
                        subjectDirectoryMaskFromMorphologist,
                        outputDirectory,
                        verbose):
    """
    fileNameDw: path to GIS shell image (e.g. .../05-GisConversion/DWI_b0500.ima)
    subjectDirectoryEddyCurrentAndMotionCorrection: we use this as 04-SplitDWIShells
       (holds t2_wo_eddy_current.ima and per-shell bval/bvec)
    """
    if verbose:
        print("LOCAL MODELING USING DTI MODEL")
        print("-------------------------------------------------------------")

    # t2_wo_eddy_current.ima lives in 04-SplitDWIShells (as requested)
    fileNameT2   = os.path.join(subjectDirectoryEddyCurrentAndMotionCorrection, 't2_wo_eddy_current.ima')
    fileNameMask = os.path.join(subjectDirectoryMaskFromMorphologist, 'mask.ima')

    # outputs
    fileNameFA                   = os.path.join(outputDirectory, 'dti_fa')
    fileNameRGB                  = os.path.join(outputDirectory, 'dti_rgb')
    fileNameADC                  = os.path.join(outputDirectory, 'dti_adc')
    fileNameParallelDiffusivity  = os.path.join(outputDirectory, 'dti_parallel_diffusivity')
    fileNameTransverseDiffusivity= os.path.join(outputDirectory, 'dti_transverse_diffusivity')

    # --- Preflight: ensure DW has gradients in MINF ---
    attrs, src_minf = _read_minf_attrs(fileNameDw)
    if not _has_gradients(attrs):
        if verbose:
            print(f"[preflight] DW header missing gradients; injecting…")
        # infer per-shell bval/bvec from *this* SplitDWIShells directory
        split_dir = subjectDirectoryEddyCurrentAndMotionCorrection  # .../<ses>/04-SplitDWIShells
        # parse tag from basename: DWI_b0500.ima -> b0500
        base = os.path.splitext(os.path.basename(fileNameDw))[0]  # DWI_b0500
        shell_tag = base.split("_")[-1] if "_" in base else ""
        bvec = os.path.join(split_dir, f"dwi_{shell_tag}.bvec")
        bval = os.path.join(split_dir, f"dwi_{shell_tag}.bval")
        shell_b = None
        if shell_tag.startswith("b"):
            try:
                shell_b = int(shell_tag[1:])
            except Exception:
                shell_b = None
        if not os.path.isfile(bvec) and verbose:
            print(f"[preflight][warn] missing {bvec}")
        _inject_gradients_with_tool(
            fileNameDw,
            bval_path=bval if os.path.isfile(bval) else None,
            bvec_path=bvec,
            shell_b=shell_b,
            verbose=verbose
        )
        # re-check
        attrs, src_minf = _read_minf_attrs(fileNameDw)
        if verbose and src_minf:
            print(f"[preflight] using MINF: {src_minf}")

    if not _has_gradients(attrs):
        print(f"[preflight][warn] gradients still not visible in MINF for {fileNameDw}; "
              f"continuing, but DwiTensorField may fail.")

    # --- Main tensor computation with mask ---
    gkg.executeCommand({
        'algorithm': 'DwiTensorField',
        'parameters': {
            'fileNameT2': str(fileNameT2),
            'fileNameDW': str(fileNameDw),
            'fileNameMask': fileNameMask,
            'tensorFunctorNames': ('fa', 'rgb', 'adc', 'lambda_parallel', 'lambda_transverse'),
            'outputFileNames': (
                fileNameFA,
                fileNameRGB,
                fileNameADC,
                fileNameParallelDiffusivity,
                fileNameTransverseDiffusivity
            ),
            'outputOrientationCount': 0,
            'radius': -1.0,
            'thresholdRatio': 0.01,
            'volumeFormat': 'gis',
            'meshMapFormat': 'aimsmesh',
            'textureMapFormat': 'aimstexture',
            'rgbScale': 1.0,
            'meshScale': 1.0,
            'lowerFAThreshold': 0.0,
            'upperFAThreshold': 1.0,
            'specificScalarParameters': (),
            'specificStringParameters': ('robust_positive_definite',),
            'ascii': False,
            'verbose': verbose
        },
        'verbose': verbose
    })

    # --- ADC without mask (legacy behavior) ---
    fileNameADCWoMask = os.path.join(outputDirectory, 'dti_adc_wo_mask')
    gkg.executeCommand({
        'algorithm': 'DwiTensorField',
        'parameters': {
            'fileNameT2': fileNameT2,
            'fileNameDW': fileNameDw,
            'fileNameMask': '',
            'tensorFunctorNames': 'adc',
            'outputFileNames': fileNameADCWoMask,
            'outputOrientationCount': 0,
            'radius': -1.0,
            'thresholdRatio': 0.01,
            'volumeFormat': 'gis',
            'meshMapFormat': 'aimsmesh',
            'textureMapFormat': 'aimstexture',
            'rgbScale': 1.0,
            'meshScale': 1.0,
            'lowerFAThreshold': 0.0,
            'upperFAThreshold': 1.0,
            'specificScalarParameters': (),
            'specificStringParameters': ('robust_positive_definite',),
            'ascii': False,
            'verbose': verbose
        },
        'verbose': verbose
    })

    if verbose:
        print("-------------------------------------------------------------")
