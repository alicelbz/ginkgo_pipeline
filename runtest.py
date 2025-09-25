#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RunPipeline.py (cleaned for NIfTI inputs)

- Starts from NIfTI laid out as:
    <inputNiftiRoot>/sub-XXXX/ses-YYYYMMDD/anat/*.nii[.gz]
    <inputNiftiRoot>/sub-XXXX/ses-YYYYMMDD/dwi/*.nii[.gz], *.bval, *.bvec, *.json
- Converts NIfTI -> GIS (02-GisConversion) using NiftiToGisConversion.runNifti2GisConversion
- Keeps the rest of the steps and numbering (04..36), but removes:
    * 01-DicomCopy
    * 03-NiftiConversion
    * differentMatrixSequences logic
"""

import os, json, sys, shutil

# Ginkgo / gkg entry points inside the container
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import *  # noqa

import numpy as np  # noqa
import matplotlib.mlab as mlab  # noqa
import matplotlib.pyplot as plt  # noqa

from CopyFileDirectoryRm import *  # noqa

# --- pipeline steps (unchanged) ---
from SusceptibilityArtifactFromTopUpCorrection import *  # noqa
from OrientationAndBValueFileDecoding import *  # noqa
from QSpaceSamplingAddition import *  # noqa
from MaskFromMorphologistPipeline import *  # noqa
from OutlierCorrection import *  # noqa
from EddyCurrentAndMotionCorrection import *  # noqa
from LocalModelingDTI import *  # noqa
from LocalModelingQBI import *  # noqa
from NoddiMicrostructureField import *  # noqa
from TractographySRD import *  # noqa
from FiberLengthHistogramSRD import *  # noqa
from LongFiberLabelling import *  # noqa
from ShortFiberLabelling import *  # noqa
from FreeSurferParcellation import *  # noqa
from DiffusionMetricsAlongBundles import *  # noqa
from DiffusionMetricsAlongCutExtremitiesBundles import *  # noqa
from DiffusionMetricsInROIs import *  # noqa
from DiffusionMetricsInHippROIs import *  # noqa
from FastSegmentation import *  # noqa
from DiffusionMetricsInWhiteGreyMatter import *  # noqa
from Normalization import *  # noqa
from ConnectivityMatrix import *  # noqa
from FullConnectivityTemplate import *  # noqa
from DiffusionMetricsInHippocampiConnectivityTemplate import *  # noqa
from DiffusionMetricsInFullConnectivityTemplate import *  # noqa
from DiffusionMetricsInConnectivityMatrix import *  # noqa
from DiffusionMetricsInMNISpace import *  # noqa
from DiffusionMetricsInCutExtremitiesConnectivityMatrix import *  # noqa

# --- new: NIfTI -> GIS conversion ---
from NiftiToGisConversion import runNifti2GisConversion  # local helper you created


# ---------------------------
# helpers
# ---------------------------

def _safe(task_dict, key, default=0):
    try:
        return int(task_dict.get(key, default))
    except Exception:
        return default


def _ensure_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
    return d


def makeDirectory(root, name):
    """Keep original helper name used throughout the pipeline modules."""
    return _ensure_dir(os.path.join(root, name))


def _subjects_from_json(subjects_json):
    """
    Accept flexible subjects.json formats:

    Option A:
      {
        "subjects": [
          {"id": "sub-PR07", "sessions": ["ses-20250106", "ses-20241219"]},
          ...
        ]
      }

    Option B (legacy):
      {
        "patients": {
          "sub-PR07": {"sessions": ["ses-20250106"]},
          "sub-PR08": {"sessions": ["ses-20250609"]}
        }
      }

    Option C (very legacy: groups -> [subject_id, ...]) is also tolerated,
    but sessions then must be inferred externally.
    """
    if isinstance(subjects_json, dict) and "subjects" in subjects_json:
        # Option A
        for rec in subjects_json["subjects"]:
            sid = rec.get("id")
            sessions = rec.get("sessions", [])
            if sid and isinstance(sessions, list):
                for ses in sessions:
                    yield sid, ses
        return

    # Option B: groups mapping to dict of subjects
    for group, entries in subjects_json.items():
        if not isinstance(entries, dict):
            # Option C (groups -> list of subjects) – no sessions info here
            if isinstance(entries, list):
                for sid in entries:
                    # no explicit sessions; skip unless provided elsewhere
                    yield sid, None
            continue
        for sid, meta in entries.items():
            if isinstance(meta, dict) and "sessions" in meta:
                for ses in meta["sessions"]:
                    yield sid, ses
            else:
                yield sid, None


def _build_description_for_conversion(nifti_session_dir):
    """
    Build the description dict for NIfTI->GIS step.
    We assume:
      anat: *T1w.nii.gz
      dwi : *dwi.nii.gz (+ bval/bvec sitting next to it for later steps)
    """
    anat_dir = os.path.join(nifti_session_dir, "anat")
    dwi_dir  = os.path.join(nifti_session_dir, "dwi")

    # Try to pick a single T1w and a single DWI volume by simple patterns
    def _pick_one(dirpath, pattern):
        if not os.path.isdir(dirpath):
            return None
        cands = [f for f in os.listdir(dirpath) if f.endswith(".nii.gz") and pattern in f]
        cands.sort()
        return cands[0] if cands else None

    t1_rel  = None
    dwi_rel = None

    t1_name  = _pick_one(anat_dir, "T1w")
    dwi_name = _pick_one(dwi_dir, "dwi")

    if t1_name:
        t1_rel = os.path.join("anat", t1_name)
    if dwi_name:
        dwi_rel = os.path.join("dwi", dwi_name)

    desc = {}
    if t1_rel:
        desc["T1w"] = t1_rel
    if dwi_rel:
        desc["DWI"] = dwi_rel

    return desc


# ---------------------------
# main pipeline
# ---------------------------

def runPipeline(inputNiftiRoot,
                subjectJsonFileName,
                taskJsonFileName,
                timePoint,              # kept for interface compatibility; not used to filter sessions
                outputDirectory,
                verbose):

    # Prepare output root
    _ensure_dir(outputDirectory)

    # Load subjects
    with open(subjectJsonFileName, "r") as f:
        subjects = json.load(f)

    # Load tasks
    with open(taskJsonFileName, "r") as f:
        taskDescription = json.load(f)

    # Connectivity directories collectors (by timepoint label if you still use V1/V2/V3)
    subjectV1ConnectivityMatrixDirectories = []
    subjectV2ConnectivityMatrixDirectories = []
    subjectV3ConnectivityMatrixDirectories = []

    # Iterate subjects/sessions from JSON
    for subject, session in _subjects_from_json(subjects):
        if session is None:
            if verbose:
                print(f"[WARN] No session listed for {subject}; skipping.")
            continue

        if verbose:
            print("===================================================")
            print(f"{subject} / {session}")
            print("===================================================")

        # NIfTI session directory (your data_in layout)
        subjectSessionDir = os.path.join(inputNiftiRoot, subject, session)
        if not os.path.isdir(subjectSessionDir):
            if verbose:
                print(f"[WARN] Missing session dir: {subjectSessionDir} -> skip.")
            continue

        # Output: <outputDirectory>/<subject>/<session>
        subjectOutputDirectoryTemp = _ensure_dir(os.path.join(outputDirectory, subject))
        subjectOutputDirectory = _ensure_dir(os.path.join(subjectOutputDirectoryTemp, session))

        # =========================
        # 02 - GIS conversion
        # =========================
        outputDirectoryGisConversion = makeDirectory(subjectOutputDirectory, "02-GisConversion")

        if _safe(taskDescription, "GisConversion", 1) == 1:
            # Build description dict from discovered files
            description = _build_description_for_conversion(subjectSessionDir)

            if verbose:
                print("[02] NIfTI -> GIS conversion")
                print("     input session:", subjectSessionDir)
                print("     map:", description)

            runNifti2GisConversion(
                subjectNiftiDirectory=subjectSessionDir,
                description=description,
                outputDirectory=outputDirectoryGisConversion,
                verbose=bool(verbose),
            )

        # =========================
        # 04 - TopUp correction (optional)
        # =========================
        outputDirectoryTopUpCorrection = makeDirectory(subjectOutputDirectory, "04-TopUpCorrection")
        if _safe(taskDescription, "TopUpCorrection", 0) == 1:
            if verbose:
                print("[04] TopUpCorrection")
            # Expect this function to read NIfTI (AP/PA pairs) directly from the session
            # and/or use the results of GIS conversion as needed.
            # If your implementation expects a different input, adjust here:
            runTopUpCorrection(
                subjectSessionDir,       # <- raw/preproc NIfTI location
                {},                      # differentTopUpAcquisitions (removed/unused; pass empty)
                timePoint,               # retained param; your function may ignore it
                outputDirectoryTopUpCorrection,
                bool(verbose)
            )

        # =========================
        # 05 - Orientation & B-Value / B-Vec decoding
        # =========================
        outputDirectoryOrientationAndBValueFileDecoding = makeDirectory(
            subjectOutputDirectory, "05-OrientationAndBValueFileDecoding"
        )
        if _safe(taskDescription, "OrientationAndBValueFileDecoding", 1) == 1:
            if verbose:
                print("[05] OrientationAndBValueFileDecoding")
            flippingTypes = ['y']  # keep previous default
            runOrientationAndBValueFileDecoding(
                outputDirectoryGisConversion,
                outputDirectoryTopUpCorrection,
                flippingTypes,
                {},  # description not needed anymore
                outputDirectoryOrientationAndBValueFileDecoding,
                bool(verbose)
            )

        # =========================
        # 06 - Q-Space sampling addition
        # =========================
        outputDirectoryQSpaceSamplingAddition = makeDirectory(subjectOutputDirectory, "06-QSpaceSamplingAddition")
        if _safe(taskDescription, "QSpaceSamplingAddition", 1) == 1:
            if verbose:
                print("[06] QSpaceSamplingAddition")
            runQSpaceSamplingAddition(
                outputDirectoryOrientationAndBValueFileDecoding,
                outputDirectoryQSpaceSamplingAddition,
                bool(verbose)
            )

        # =========================
        # 07 - Mask from Morphologist (needs T1 from 02)
        # =========================
        outputDirectoryMaskFromMorphologist = makeDirectory(subjectOutputDirectory, "07-MaskFromMorphologistPipeline")
        if _safe(taskDescription, "Morphologist", 1) == 1:
            if verbose:
                print("[07] MaskFromMorphologistPipeline")
            fileNameT1APC = os.path.join(outputDirectoryGisConversion, 'T1w.APC')
            runMaskFromMorphologistPipeline(
                outputDirectoryGisConversion,
                outputDirectoryQSpaceSamplingAddition,
                fileNameT1APC,
                outputDirectoryMaskFromMorphologist,
                bool(verbose)
            )

        # =========================
        # 08 - Outlier correction
        # =========================
        outputDirectoryOutlierCorrection = makeDirectory(subjectOutputDirectory, "08-OutlierCorrection")
        if _safe(taskDescription, "OutlierCorrection", 1) == 1:
            if verbose:
                print("[08] OutlierCorrection")
            runOutlierCorrection(
                outputDirectoryQSpaceSamplingAddition,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryOutlierCorrection,
                bool(verbose)
            )

        # =========================
        # 09 - Eddy current & motion correction
        # =========================
        outputDirectoryEddy = makeDirectory(subjectOutputDirectory, "09-EddyCurrentAndMotionCorrection")
        if _safe(taskDescription, "EddyCurrentCorrection", 1) == 1:
            if verbose:
                print("[09] EddyCurrentAndMotionCorrection")
            runEddyCurrentAndMotionCorrection(
                outputDirectoryOutlierCorrection,
                outputDirectoryMaskFromMorphologist,
                outputDirectoryEddy,
                bool(verbose)
            )

        # =========================
        # local modeling inputs
        # =========================
        # Multiple-shell aggregate
        fileNameDw = os.path.join(outputDirectoryEddy, "dw_wo_eddy_current.ima")
        # Per-shell (if your pipeline produces these names)
        fileNameDwShell1 = os.path.join(outputDirectoryEddy, "dw_shell1.ima")
        fileNameDwShell2 = os.path.join(outputDirectoryEddy, "dw_shell2.ima")
        fileNameDwShell3 = os.path.join(outputDirectoryEddy, "dw_shell3.ima")

        # 10–12 DTI per-shell
        if _safe(taskDescription, "LocalModelingDTI-B0200", 0) == 1:
            outDTI1 = makeDirectory(subjectOutputDirectory, "10-LocalModeling-DTI-B0200")
            if verbose: print("[10] LocalModelingDTI-B0200")
            runLocalModelingDTI(fileNameDwShell1, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outDTI1, bool(verbose))

        if _safe(taskDescription, "LocalModelingDTI-B1500", 0) == 1:
            outDTI2 = makeDirectory(subjectOutputDirectory, "11-LocalModeling-DTI-B1500")
            if verbose: print("[11] LocalModelingDTI-B1500")
            runLocalModelingDTI(fileNameDwShell2, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outDTI2, bool(verbose))

        if _safe(taskDescription, "LocalModelingDTI-B2500", 0) == 1:
            outDTI3 = makeDirectory(subjectOutputDirectory, "12-LocalModeling-DTI-B2500")
            if verbose: print("[12] LocalModelingDTI-B2500")
            runLocalModelingDTI(fileNameDwShell3, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outDTI3, bool(verbose))

        # 13 DTI multi-shell
        if _safe(taskDescription, "LocalModelingDTI-Multiple-Shell", 1) == 1:
            outDTIall = makeDirectory(subjectOutputDirectory, "13-LocalModeling-DTI-Multiple-Shell")
            if verbose: print("[13] LocalModelingDTI-Multiple-Shell")
            runLocalModelingDTI(fileNameDw, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outDTIall, bool(verbose))

        # 14–16 QBI per-shell
        if _safe(taskDescription, "LocalModelingQBI-B0200", 0) == 1:
            outQBI1 = makeDirectory(subjectOutputDirectory, "14-LocalModeling-QBI-B0200")
            if verbose: print("[14] LocalModelingQBI-B0200")
            runLocalModelingQBI(fileNameDwShell1, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outQBI1, bool(verbose))

        if _safe(taskDescription, "LocalModelingQBI-B1500", 0) == 1:
            outQBI2 = makeDirectory(subjectOutputDirectory, "15-LocalModeling-QBI-B1500")
            if verbose: print("[15] LocalModelingQBI-B1500")
            runLocalModelingQBI(fileNameDwShell2, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outQBI2, bool(verbose))

        if _safe(taskDescription, "LocalModelingQBI-B2500", 0) == 1:
            outQBI3 = makeDirectory(subjectOutputDirectory, "16-LocalModeling-QBI-B2500")
            if verbose: print("[16] LocalModelingQBI-B2500")
            runLocalModelingQBI(fileNameDwShell3, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outQBI3, bool(verbose))

        # 17 QBI multi-shell
        if _safe(taskDescription, "LocalModelingQBI-Multiple-Shell", 1) == 1:
            outQBIall = makeDirectory(subjectOutputDirectory, "17-LocalModeling-QBI-Multiple-Shell")
            if verbose: print("[17] LocalModelingQBI-Multiple-Shell")
            runLocalModelingQBI(fileNameDw, outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outQBIall, bool(verbose))

        # 18 NODDI
        if _safe(taskDescription, "NoddiMicrostructureField", 1) == 1:
            outNODDI = makeDirectory(subjectOutputDirectory, "18-NoddiMicrostructureField")
            if verbose: print("[18] NoddiMicrostructureField")
            runNoddiMicrostructureField(outputDirectoryEddy, outputDirectoryMaskFromMorphologist, outNODDI, bool(verbose))

        # 19 Tractography SRD
        if _safe(taskDescription, "TractographySRD", 1) == 1:
            outSRD = makeDirectory(subjectOutputDirectory, "19-Tractography-SRD")
            if verbose: print("[19] Tractography-SRD")
            # Using highest-shell QBI by default; adjust if needed
            runTractographySRD(outQBI3 if 'outQBI3' in locals() else outQBIall,  # prefer high-b QBI; else multi-shell
                               outputDirectoryMaskFromMorphologist,
                               outSRD,
                               bool(verbose))

        # 20 Fiber length histogram (SRD)
        if _safe(taskDescription, "FiberLengthHistogramSRD", 1) == 1:
            outFLH = makeDirectory(subjectOutputDirectory, "20-FiberLengthHistogram-SRD")
            if verbose: print("[20] FiberLengthHistogram-SRD")
            runFiberLengthHistogramSRD(outSRD, outFLH, bool(verbose))

        # 21 Long fiber labelling (SRD)
        if _safe(taskDescription, "LongFiberLabellingSRD", 1) == 1:
            outLong = makeDirectory(subjectOutputDirectory, "21-LongFiberLabellingSRD")
            if verbose: print("[21] LongFiberLabellingSRD")
            runLongFiberLabelling(outSRD, outputDirectoryMaskFromMorphologist, outLong, bool(verbose))

        # 22 Short fiber labelling (SRD)
        if _safe(taskDescription, "ShortFiberLabellingSRD", 1) == 1:
            outShort = makeDirectory(subjectOutputDirectory, "22-ShortFiberLabellingSRD")
            if verbose: print("[22] ShortFiberLabellingSRD")
            runShortFiberLabelling(outSRD, outputDirectoryMaskFromMorphologist, outShort, bool(verbose))

        # 23 metrics along long bundles (SRD)
        if _safe(taskDescription, "DiffusionMetricsAlongLongBundlesSRD", 1) == 1:
            outMetLong = makeDirectory(subjectOutputDirectory, "23-DiffusionMetricsAlongLongBundlesSRD")
            if verbose: print("[23] DiffusionMetricsAlongLongBundlesSRD")
            runDiffusionMetricsAlongBundles(outLong,
                                            outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                            outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                            outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                            outputDirectoryMaskFromMorphologist,
                                            outMetLong,
                                            bool(verbose))

        # 23b metrics along cut extremities long bundles (SRD)
        if _safe(taskDescription, "DiffusionMetricsAlongCutExtremitiesLongBundlesSRD", 0) == 1:
            outMetLongCut = makeDirectory(subjectOutputDirectory, "23-DiffusionMetricsAlongCutExtremitiesLongBundlesSRD")
            if verbose: print("[23b] DiffusionMetricsAlongCutExtremitiesLongBundlesSRD")
            runDiffusionMetricsAlongCutExtremitiesBundles(outLong,
                                                          outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                                          outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                                          outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                                          outputDirectoryMaskFromMorphologist,
                                                          outMetLongCut,
                                                          bool(verbose))

        # 24 metrics along short bundles (SRD)
        if _safe(taskDescription, "DiffusionMetricsAlongShortBundlesSRD", 1) == 1:
            outMetShort = makeDirectory(subjectOutputDirectory, "24-DiffusionMetricsAlongShortBundlesSRD")
            if verbose: print("[24] DiffusionMetricsAlongShortBundlesSRD")
            runDiffusionMetricsAlongBundles(outShort,
                                            outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                            outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                            outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                            outputDirectoryMaskFromMorphologist,
                                            outMetShort,
                                            bool(verbose))

        # 24b metrics along cut extremities short bundles (SRD)
        if _safe(taskDescription, "DiffusionMetricsAlongCutExtremitiesShortBundlesSRD", 0) == 1:
            outMetShortCut = makeDirectory(subjectOutputDirectory, "24-DiffusionMetricsAlongCutExtremitiesShortBundlesSRD")
            if verbose: print("[24b] DiffusionMetricsAlongCutExtremitiesShortBundlesSRD")
            runDiffusionMetricsAlongCutExtremitiesBundles(outShort,
                                                          outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                                          outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                                          outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                                          outputDirectoryMaskFromMorphologist,
                                                          outMetShortCut,
                                                          bool(verbose))

        # 25 FreeSurfer parcellation
        if _safe(taskDescription, "FreesurferParcellation", 1) == 1:
            outFS = makeDirectory(subjectOutputDirectory, "25-FreeSurferParcellation")
            if verbose: print("[25] FreeSurferParcellation")
            runFreeSurferParcellation(outputDirectoryMaskFromMorphologist, subject, outFS, bool(verbose))

        # 26 metrics in ROIs
        if _safe(taskDescription, "DiffusionMetricsInROIs", 1) == 1:
            outMetROIs = makeDirectory(subjectOutputDirectory, "26-DiffusionMetricsInROIs")
            if verbose: print("[26] DiffusionMetricsInROIs")
            runDiffusionMetricsInROIs(outFS,
                                      outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                      outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                      outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                      outputDirectoryMaskFromMorphologist,
                                      outMetROIs,
                                      bool(verbose))

        # 27 FAST segmentation
        if _safe(taskDescription, "FastSegmentation", 1) == 1:
            outFAST = makeDirectory(subjectOutputDirectory, "27-FastSegmentation")
            if verbose: print("[27] FastSegmentation")
            runFASTSegmentation(outputDirectoryMaskFromMorphologist, outFAST, bool(verbose))

        # 28 metrics in white/grey matter
        if _safe(taskDescription, "DiffusionMetricsInWhiteGreyMatter", 1) == 1:
            outMetWMGM = makeDirectory(subjectOutputDirectory, "28-DiffusionMetricsInWhiteGreyMatter")
            if verbose: print("[28] DiffusionMetricsInWhiteGreyMatter")
            runDiffusionMetricsInWhiteGreyMatter(outFAST,
                                                 outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                                 outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                                 outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                                 outputDirectoryMaskFromMorphologist,
                                                 outMetWMGM,
                                                 bool(verbose))

        # 29 metrics in hippocampal ROIs
        if _safe(taskDescription, "DiffusionMetricsInHippROIs", 1) == 1:
            outMetHipp = makeDirectory(subjectOutputDirectory, "29-DiffusionMetricsInHippROIs")
            if verbose: print("[29] DiffusionMetricsInHippROIs")
            runDiffusionMetricsInHippROIs(outFS,
                                          outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                                          outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                                          outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                                          outputDirectoryMaskFromMorphologist,
                                          outMetHipp,
                                          bool(verbose))

        # 30 normalization (MNI template already placed at /work/templates/mni_icbm152_nlin_asym_09a)
        if _safe(taskDescription, "Normalization", 1) == 1:
            outNorm = makeDirectory(subjectOutputDirectory, "30-Normalization")
            templateDirectory = "/work/templates/mni_icbm152_nlin_asym_09a"
            if verbose: print("[30] Normalization (MNI)")
            runNormalization(outputDirectoryMaskFromMorphologist, templateDirectory, outNorm, bool(verbose))

        # 31 connectivity matrix
        if _safe(taskDescription, "ConnectivityMatrix", 1) == 1:
            outConn = makeDirectory(subjectOutputDirectory, "31-ConnectivityMatrix")
            if verbose: print("[31] ConnectivityMatrix")
            runConnectivityMatrix(
                outSRD,
                outputDirectoryMaskFromMorphologist,
                outFS,
                outNorm if 'outNorm' in locals() else None,
                outConn,
                bool(verbose)
            )

            # Optional: keep per-timepoint arrays, if you still use V1/V2/V3 labeling
            if session == 'V1':
                subjectV1ConnectivityMatrixDirectories.append(outConn)
            elif session == 'V2':
                subjectV2ConnectivityMatrixDirectories.append(outConn)
            else:
                subjectV3ConnectivityMatrixDirectories.append(outConn)

        # 32 template metrics (hippocampi)
        if _safe(taskDescription, "DiffusionMetricsInHippocampiConnectivityTemplate", 1) == 1:
            outHippTpl = makeDirectory(subjectOutputDirectory, "32-DiffusionMetricsInHippocampiConnectivityTemplate")
            if verbose: print("[32] DiffusionMetricsInHippocampiConnectivityTemplate")
            # This needs the global template built below; it runs after that block in the original
            # We keep call signature for compatibility; the module will handle inputs.
            runDiffusionMetricsInHippocampiConnectivityTemplate(
                None,  # full template path is provided in the second pass below, kept for compatibility
                outDTIall if 'outDTIall' in locals() else outputDirectoryEddy,
                outQBIall if 'outQBIall' in locals() else outputDirectoryEddy,
                outNODDI if 'outNODDI' in locals() else outputDirectoryEddy,
                outputDirectoryMaskFromMorphologist,
                outNorm if 'outNorm' in locals() else None,
                outHippTpl,
                bool(verbose)
            )

        # 33 full connectivity template metrics (second pass below will provide the template)
        if _safe(taskDescription, "DiffusionMetricsInFullConnectivityTemplate", 1) == 1:
            makeDirectory(subjectOutputDirectory, "33-DiffusionMetricsInFullConnectivityTemplate")

        # 34 metrics in connectivity matrix space
        if _safe(taskDescription, "DiffusionMetricsInConnectivityMatrix", 1) == 1:
            makeDirectory(subjectOutputDirectory, "34-DiffusionMetricsInConnectivityMatrix")

        # 35 metrics in MNI space
        if _safe(taskDescription, "DiffusionMetricsInMNISpace", 1) == 1:
            makeDirectory(subjectOutputDirectory, "35-DiffusionMetricsInMNISpace")

        # 36 metrics in cut-extremities connectivity matrix
        if _safe(taskDescription, "DiffusionMetricsInCutExtremitiesConnectivityMatrix", 1) == 1:
            makeDirectory(subjectOutputDirectory, "36-DiffusionMetricsInCutExtremitiesConnectivityMatrix")

    # ============================================================
    # Global templates (full connectivity template) + second passes
    # ============================================================

    # 00 - Full connectivity template (global across subjects)
    outputDirectoryFullConnectivityTemplate = makeDirectory(outputDirectory, "00-FullConnectivityTemplate")
    if _safe(taskDescription, "FullConnectivityTemplate", 1) == 1:
        runFullConnectivityTemplate(subjectV1ConnectivityMatrixDirectories,
                                    subjectV2ConnectivityMatrixDirectories,
                                    subjectV3ConnectivityMatrixDirectories,
                                    outputDirectoryFullConnectivityTemplate,
                                    bool(verbose))

    # Second loops to compute metrics in templates using the built full template
    # (kept to match the original structure)
    for subject, session in _subjects_from_json(subjects):
        if session is None:
            continue

        subjectOutputDirectory = os.path.join(outputDirectory, subject, session)
        if not os.path.isdir(subjectOutputDirectory):
            continue

        if bool(verbose):
            print("===================================================")
            print(f"[2nd pass] {subject} / {session}")
            print("===================================================")

        outDTIall = os.path.join(subjectOutputDirectory, '13-LocalModeling-DTI-Multiple-Shell')
        outQBIall = os.path.join(subjectOutputDirectory, '17-LocalModeling-QBI-Multiple-Shell')
        outNODDI  = os.path.join(subjectOutputDirectory, '18-NoddiMicrostructureField')
        outMask   = os.path.join(subjectOutputDirectory, '07-MaskFromMorphologistPipeline')
        outNorm   = os.path.join(subjectOutputDirectory, '30-Normalization')
        outConn   = os.path.join(subjectOutputDirectory, '31-ConnectivityMatrix')

        # 32 Hippocampi template metrics
        if _safe(taskDescription, "DiffusionMetricsInHippocampiConnectivityTemplate", 1) == 1:
            outHippTpl = makeDirectory(subjectOutputDirectory, "32-DiffusionMetricsInHippocampiConnectivityTemplate")
            runDiffusionMetricsInHippocampiConnectivityTemplate(
                outputDirectoryFullConnectivityTemplate,
                outDTIall, outQBIall, outNODDI,
                outMask, outNorm, outHippTpl, bool(verbose)
            )

        # 33 Full connectivity template metrics
        if _safe(taskDescription, "DiffusionMetricsInFullConnectivityTemplate", 1) == 1:
            outFullTpl = makeDirectory(subjectOutputDirectory, "33-DiffusionMetricsInFullConnectivityTemplate")
            runDiffusionMetricsInFullConnectivityTemplate(
                outputDirectoryFullConnectivityTemplate,
                outDTIall, outQBIall, outNODDI,
                outMask, outNorm, outFullTpl, bool(verbose)
            )

        # 34 Matrix-space metrics
        if _safe(taskDescription, "DiffusionMetricsInConnectivityMatrix", 1) == 1:
            outInMatrix = makeDirectory(subjectOutputDirectory, "34-DiffusionMetricsInConnectivityMatrix")
            runDiffusionMetricsInConnectivityMatrix(
                outConn, outDTIall, outQBIall, outNODDI, outMask, outInMatrix, bool(verbose)
            )

        # 35 MNI-space metrics
        if _safe(taskDescription, "DiffusionMetricsInMNISpace", 1) == 1:
            outMNISpace = makeDirectory(subjectOutputDirectory, "35-DiffusionMetricsInMNISpace")
            templateDirectory = "/work/templates/mni_icbm152_nlin_asym_09a"
            runDiffusionMetricsInMNISpace(
                templateDirectory,
                outDTIall, outQBIall, outNODDI, outMask, outNorm,
                outMNISpace, bool(verbose)
            )

        # 36 Cut-extremities connectivity-matrix metrics
        if _safe(taskDescription, "DiffusionMetricsInCutExtremitiesConnectivityMatrix", 1) == 1:
            outCEMatrix = makeDirectory(subjectOutputDirectory, "36-DiffusionMetricsInCutExtremitiesConnectivityMatrix")
            runDiffusionMetricsInConnectivityMatrix(
                outConn, outDTIall, outQBIall, outNODDI, outMask, outCEMatrix, bool(verbose)
            )
