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
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        if verbose:
            print(f"[inject][warn] injector failed: {e}")
        return False


def _write_minf_from_bvec_bval(ima_path, bval_path, bvec_path, shell_b=None, verbose=False):
    """Directly write MINF sidecars from bvec/bval files (fallback).
    Returns True on success, False otherwise.
    """
    try:
        # Read bvecs (3 rows: x, y, z)
        with open(bvec_path, "r") as f:
            rows = [ln.strip().split() for ln in f if ln.strip()]
        if len(rows) < 3:
            if verbose: print(f"[fallback] invalid bvec: {bvec_path}")
            return False
        grads = list(map(list, zip(*[[float(x) for x in row] for row in rows])))

        # Read bvals
        if bval_path and os.path.isfile(bval_path):
            with open(bval_path, "r") as f:
                bvals = [float(x) for x in f.read().strip().split()]
        elif shell_b is not None:
            bvals = [float(shell_b)] * len(grads)
        else:
            if verbose: print(f"[fallback] missing bval and no shell_b provided")
            return False

        if len(bvals) != len(grads):
            if verbose: print(f"[fallback] bval/bvec length mismatch: {len(bvals)} vs {len(grads)}")
            return False

        attrs = {
            'diffusion_gradient_orientations': grads,
            'diffusion_b_values': bvals,
        }
        body = "attributes = " + repr(attrs) + "\n"

        base, ext = os.path.splitext(ima_path)
        minf_dim = base + ".dim.minf"
        minf_raw = base + ".minf"
        minf_ima = ima_path + ".minf"
        for p in (minf_dim, minf_raw, minf_ima):
            with open(p, "w") as f:
                f.write(body)
            if verbose:
                print(f"[fallback] wrote {p}")
        return True
    except Exception as e:
        if verbose:
            print(f"[fallback] exception while writing MINF: {e}")
        return False


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
    print("*** ENTERING LocalModelingDTI with:", fileNameDw)
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
        injected = _inject_gradients_with_tool(
            fileNameDw,
            bval_path=bval if os.path.isfile(bval) else None,
            bvec_path=bvec,
            shell_b=shell_b,
            verbose=verbose
        )
        if not injected:
            if verbose:
                print("[preflight] injector failed, attempting direct MINF write fallback")
            _write_minf_from_bvec_bval(
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

    # --- FORCE gradients into GIS header using Combiner workaround ---
    temp_dw_with_gradients = fileNameDw  # default to original
    try:
        attrs, _ = _read_minf_attrs(fileNameDw)
        if _has_gradients(attrs):
            if verbose:
                print(f"[force-inject] creating temp DW with embedded gradients")
            
            # Create a temporary file with embedded gradients using Combiner
            temp_dw_with_gradients = fileNameDw.replace('.ima', '_with_gradients.ima')
            
            # First copy the file using Combiner (this preserves most metadata)
            gkg.executeCommand({
                'algorithm': 'Combiner',
                'parameters': {
                    'fileNameIns': str(fileNameDw),
                    'fileNameOut': str(temp_dw_with_gradients),
                    'functor1s': 'id',
                    'functor2s': 'id', 
                    'numerator1s': (1.0, 1.0),
                    'denominator1s': (1.0, 1.0),
                    'numerator2s': 1.0,
                    'denominator2s': 1.0,
                    'operators': '*',
                    'fileNameMask': '',
                    'mode': 'gt',
                    'threshold1': 0.0,
                    'threshold2': 0.0,
                    'background': 0.0,
                    'outputType': 'float',
                    'ascii': False,
                    'format': 'gis',
                    'verbose': verbose,
                },
                'verbose': verbose
            })
            
            # Write all MINF variants for the temp file
            _write_minf_from_bvec_bval(
                temp_dw_with_gradients,
                bval_path=bval if os.path.isfile(bval) else None,
                bvec_path=bvec,
                shell_b=shell_b,
                verbose=verbose
            )
            
            if verbose:
                print(f"[force-inject] using temp file with gradients: {temp_dw_with_gradients}")
                print(f"[force-inject] temp file exists: {os.path.exists(temp_dw_with_gradients)}")
    except Exception as e:
        if verbose:
            print(f"[force-inject][warn] failed to create temp file: {e}")
        temp_dw_with_gradients = fileNameDw  # fallback to original

    if verbose:
        print(f"[DEBUG] Final DW file to use: {temp_dw_with_gradients}")
        print(f"[DEBUG] DW file exists: {os.path.exists(temp_dw_with_gradients)}")

    # --- Main tensor computation with mask ---
    gkg.executeCommand({
        'algorithm': 'DwiTensorField',
        'parameters': {
            'fileNameT2': str(fileNameT2),
            'fileNameDW': str(temp_dw_with_gradients),  # Use temp file if created
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
            'fileNameDW': temp_dw_with_gradients,  # Use temp file if created
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

    # --- Cleanup temp file if created ---
    if temp_dw_with_gradients != fileNameDw:
        try:
            os.remove(temp_dw_with_gradients)
            os.remove(temp_dw_with_gradients.replace('.ima', '.dim'))
            for ext in ['.dim.minf', '.ima.minf', '.minf']:
                temp_minf = temp_dw_with_gradients.replace('.ima', ext)
                if os.path.exists(temp_minf):
                    os.remove(temp_minf)
            if verbose:
                print(f"[cleanup] removed temp file: {temp_dw_with_gradients}")
        except Exception as e:
            if verbose:
                print(f"[cleanup][warn] failed to remove temp files: {e}")

    if verbose:
        print("-------------------------------------------------------------")
