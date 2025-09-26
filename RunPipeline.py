import os, json, sys, shutil
import os, json, sys, shutil


sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import *

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from CopyFileDirectoryRm import *

from SusceptibilityArtifactFromTopUpCorrection import *
from OrientationAndBValueFileDecoding import *
from QSpaceSamplingAddition import *
from MaskFromMorphologistPipeline import *
from OutlierCorrection import *
from EddyCurrentAndMotionCorrection import *
from LocalModelingDTI import *
from LocalModelingQBI import *
from NoddiMicrostructureField import *
from TractographySRD import *
from FiberLengthHistogramSRD import *
from LongFiberLabelling import *
from ShortFiberLabelling import *
from FreeSurferParcellation import *
from DiffusionMetricsAlongBundles import *
from DiffusionMetricsAlongCutExtremitiesBundles import *
from DiffusionMetricsInROIs import *
from DiffusionMetricsInHippROIs import *
from FastSegmentation import *
from DiffusionMetricsInWhiteGreyMatter import *
from Normalization import *
from ConnectivityMatrix import *
from FullConnectivityTemplate import *
from DiffusionMetricsInHippocampiConnectivityTemplate import *
from DiffusionMetricsInFullConnectivityTemplate import *
from DiffusionMetricsInConnectivityMatrix import *
from DiffusionMetricsInMNISpace import *
from DiffusionMetricsInCutExtremitiesConnectivityMatrix import *

from NiftiToGisConversion import runNifti2GisConversion
from FieldmapCorrection import runFieldmapCorrection

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
    return _ensure_dir(os.path.join(root, name))


def _subjects_from_json(subjects_json):
    """
    Accept flexible subjects.json formats and yield (subject_id, session_id).

    Supported examples:
      A) {"subjects": [{"id": "sub-PR07", "sessions": ["ses-20250106"]}, ...]}
      B) {"patients": {"sub-PR07": ["ses-20250106", "ses-20241219"], ...}}
      C) {"patients": {"sub-PR07": {"sessions": ["ses-20250106"]}, ...}}
      D) {"patients": ["sub-PR07", "sub-PR08"]}  # no session info
    """

    # Option A: {"subjects": [ { "id":..., "sessions":[...] }, ... ]}
    if isinstance(subjects_json, dict) and "subjects" in subjects_json and isinstance(subjects_json["subjects"], list):
        for rec in subjects_json["subjects"]:
            sid = rec.get("id")
            sessions = rec.get("sessions", [])
            if sid and isinstance(sessions, list) and sessions:
                for ses in sessions:
                    yield sid, ses
            elif sid:
                yield sid, None
        return

    # Options B/C/D under arbitrary group keys
    for _, entries in subjects_json.items():
        # D) groups -> list of subject ids (no sessions)
        if isinstance(entries, list) and all(isinstance(x, str) for x in entries):
            for sid in entries:
                yield sid, None
            continue

        # B/C) groups -> dict of subject -> sessions/list or meta dict
        if isinstance(entries, dict):
            for sid, meta in entries.items():
                # B) subject -> [ "ses-..." , ... ]
                if isinstance(meta, list) and all(isinstance(x, str) for x in meta):
                    for ses in meta:
                        yield sid, ses
                # C) subject -> { "sessions": [...] , ... }
                elif isinstance(meta, dict) and "sessions" in meta and isinstance(meta["sessions"], list):
                    for ses in meta["sessions"]:
                        yield sid, ses
                else:
                    # subject present, but no explicit sessions
                    yield sid, None



def _build_description_for_conversion(nifti_session_dir):

    anat_dir = os.path.join(nifti_session_dir, "anat")
    dwi_dir  = os.path.join(nifti_session_dir, "dwi")

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

def runPipeline(inputNiftiRoot, subjectJsonFileName, taskJsonFileName, session, outputDirectory, verbose):
    _ensure_dir(outputDirectory)

    ##############################################################################
    # reading subject information
    ##############################################################################
    if not os.path.isdir(outputDirectory):
        os.makedirs(outputDirectory, exist_ok=True)

     # Load subjects
    with open(subjectJsonFileName, "r") as f:
        subjects = json.load(f)

    # Load tasks
    with open(taskJsonFileName, "r") as f:
        taskDescription = json.load(f)

    ##############################################################################
    # first loop over groups and individuals to perform individual processing
    ##############################################################################

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

                # Step 00: Fieldmap-based correction (produces dwi_fmapcorr.nii.gz)
                #outputDirectoryFieldmap = makeDirectory(subjectOutputDirectory, "00-FieldmapCorrection")
                #runFieldmapCorrection(
                #    subjectSessionDir=os.path.join(inputNiftiRoot, subject, timepoint),
                #    outputDirectory=outputDirectoryFieldmap,
                #    verbose=verbose,
                #    manufacturer="generic",  # GE -> "generic"; Siemens -> "SIEMENS"
                #)

                # =========================
                # GIS conversion (T1 + per-shell DWI only)
                # =========================
                outputDirectoryGisConversion = makeDirectory(subjectOutputDirectory, "01-GisConversion")

                if _safe(taskDescription, "GisConversion", 0) == 1:
                    # Always convert T1w (Morphologist needs GIS T1)
                    description = {
                        "T1w": "anat/T1w.nii.gz",
                    }

                    # Convert ONLY the split shells (no full DWI)
                    split_dir = outputDirectorySplitShells
                    for tag in ("b0000", "b0500", "b1000", "b2000", "b3000"):
                        cand = os.path.join(split_dir, f"dwi_{tag}.nii.gz")
                        if os.path.isfile(cand):
                            # e.g., DWI_B1000.ima
                            description[f"DWI_{tag.upper()}"] = cand

                    if verbose:
                        print("[01] NIfTI -> GIS conversion (T1 + per-shell only)")
                        print("     input session:", subjectSessionDir)
                        print("     map:", description)

                    runNifti2GisConversion(
                        subjectNiftiDirectory=subjectSessionDir,
                        description=description,
                        outputDirectory=outputDirectoryGisConversion,
                        verbose=bool(verbose),
                    )

                
                ##########################################################################
                # TopUp correction
                ##########################################################################

                outputDirectoryTopUpCorrection = makeDirectory(subjectOutputDirectory,
                                                               "02-TopUpCorrection")

                if _safe(taskDescription, "TopUpCorrection", 0) == 1:
                    runTopUpCorrection(subjectSessionDir,
                                       session,
                                       outputDirectoryTopUpCorrection,
                                       verbose)

                ##########################################################################
                # running orientation and b-value file decoding
                ##########################################################################

                outputDirectoryOrientationAndBValueFileDecoding = \
                    makeDirectory(subjectOutputDirectory,
                                  "03-OrientationAndBValueFileDecoding")

                flippingTypes = ['y']

                if _safe(taskDescription, "OrientationAndBValueFileDecoding", 0) == 1:
                    flippingTypes = ['y']
                    runOrientationAndBValueFileDecoding(
                        outputDirectoryGisConversion,
                        outputDirectoryTopUpCorrection,
                        flippingTypes,
                        outputDirectoryOrientationAndBValueFileDecoding,
                        verbose)

                ##########################################################################
                # running q-space sampling addition
                ##########################################################################

                outputDirectoryQSpaceSamplingAddition = makeDirectory( \
                    subjectOutputDirectory,
                    "04-QSpaceSamplingAddition")

                if _safe(taskDescription, "QSpaceSamplingAddition", 0) == 1:
                    runQSpaceSamplingAddition(
                        outputDirectoryOrientationAndBValueFileDecoding,
                        outputDirectoryQSpaceSamplingAddition,
                        verbose)

                ##########################################################################
                # running mask from Morphologist
                ##########################################################################

                outputDirectoryMaskFromMorphologist = makeDirectory( \
                    subjectOutputDirectory,
                    "05-MaskFromMorphologistPipeline")

                fileNameT1APC = os.path.join(outputDirectoryGisConversion, 'T1w.APC')


                if _safe(taskDescription, "Morphologist", 0) == 1:
                    runMaskFromMorphologistPipeline(outputDirectoryGisConversion,
                                                    outputDirectoryQSpaceSamplingAddition,
                                                    fileNameT1APC,
                                                    outputDirectoryMaskFromMorphologist,
                                                    verbose)

                ##########################################################################
                # running outlier correction
                ##########################################################################

                outputDirectoryOutlierCorrection = makeDirectory( \
                    subjectOutputDirectory,
                    "06-OutlierCorrection")

                if _safe(taskDescription, "OutlierCorrection", 0) == 1:
                    runOutlierCorrection(outputDirectoryQSpaceSamplingAddition,
                                         outputDirectoryMaskFromMorphologist,
                                         outputDirectoryOutlierCorrection,
                                         verbose)

                ##########################################################################
                # running eddy current and motion correction
                ##########################################################################

                outputDirectoryEddyCurrentAndMotionCorrection = makeDirectory( \
                    subjectOutputDirectory,
                    "07-EddyCurrentAndMotionCorrection")

                if _safe(taskDescription, "EddyCurrentCorrection", 0) == 1:
                    runEddyCurrentAndMotionCorrection(
                        outputDirectoryOutlierCorrection,
                        outputDirectoryMaskFromMorphologist,
                        outputDirectoryEddyCurrentAndMotionCorrection,
                        verbose)

                ##########################################################################
                # running DTI local modeling for b=500s/mm2
                ##########################################################################

                outputDirectoryLocalModelingDTIShell1 = makeDirectory(
                    subjectOutputDirectory,
                    "08-LocalModeling-DTI-B0500")
                fileNameDwShell1 = os.path.join(
                    outputDirectoryEddyCurrentAndMotionCorrection,
                    "dw_shell1.ima")
                
                if _safe(taskDescription, "LocalModelingDTI-B0500", 0) == 1:
                    runLocalModelingDTI(fileNameDwShell1,
                                        outputDirectoryEddyCurrentAndMotionCorrection,
                                        outputDirectoryMaskFromMorphologist,
                                        outputDirectoryLocalModelingDTIShell1,
                                        verbose)

                ##########################################################################
                # running DTI local modeling for b=1000s/mm2
                ##########################################################################

                outputDirectoryLocalModelingDTIShell2 = makeDirectory(
                    subjectOutputDirectory,
                    "09-LocalModeling-DTI-B1000")
                fileNameDwShell2 = os.path.join(
                    outputDirectoryEddyCurrentAndMotionCorrection,
                    "dw_shell2.ima")

                if _safe(taskDescription, "LocalModelingDTI-B1000", 0) == 1:
                    runLocalModelingDTI(fileNameDwShell2,
                                        outputDirectoryEddyCurrentAndMotionCorrection,
                                        outputDirectoryMaskFromMorphologist,
                                        outputDirectoryLocalModelingDTIShell2,
                                        verbose)

                ################################################################
                # running DTI local modeling for b=2000s/mm2
                ################################################################

                outputDirectoryLocalModelingDTIShell3 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "10-LocalModeling-DTI-B2000" )
                fileNameDwShell3 = os.path.join(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  "dw_shell3.ima")

                if _safe(taskDescription, "LocalModelingDTI-B2000", 0) == 1:
                    runLocalModelingDTI(
                                  fileNameDwShell3,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingDTIShell3,
                                  verbose )
                    
                ################################################################
                # running DTI local modeling for b=3000s/mm2
                ################################################################

                outputDirectoryLocalModelingDTIShell4 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "11-LocalModeling-DTI-B3000" )
                fileNameDwShell4 = os.path.join(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  "dw_shell3.ima")

                if _safe(taskDescription, "LocalModelingDTI-B3000", 0) == 1:
                    runLocalModelingDTI(
                                  fileNameDwShell4,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingDTIShell4,
                                  verbose )

                ################################################################
                # running DTI local modeling
                ################################################################

                outputDirectoryLocalModelingDTIMultipleShell = makeDirectory(
                                         subjectOutputDirectory,
                                         "12-LocalModeling-DTI-Multiple-Shell" )

                fileNameDw = os.path.join(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  "dw_wo_eddy_current.ima")
                
                if _safe(taskDescription, "LocalModelingDTI-Multiple-Shell", 0) == 1:
                    runLocalModelingDTI( 
                                  fileNameDw,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  verbose )

                ################################################################
                # running QBI local modeling for b=500s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell1 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "13-LocalModeling-QBI-B0500" )

                if _safe(taskDescription, "LocalModelingQBI-B0500", 0) == 1:
                  runLocalModelingQBI( 
                                  fileNameDwShell1,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell1,
                                  verbose )

                ################################################################
                # running QBI local modeling for b=1000s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell2 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "14-LocalModeling-QBI-B1500" )

                if _safe(taskDescription, "LocalModelingQBI-B1000", 0) == 1:
                  runLocalModelingQBI( 
                                  fileNameDwShell2,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell2,
                                  verbose )

                ################################################################
                # running QBI local modeling for b=2000s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell3 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "15-LocalModeling-QBI-B2000" )

                if _safe(taskDescription, "LocalModelingQBI-B2000", 0) == 1:
                    runLocalModelingQBI( 
                                  fileNameDwShell3,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell3,
                                  verbose)

                ################################################################
                # running QBI local modeling for b=3000s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell4 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "16-LocalModeling-QBI-B3000" )

                if _safe(taskDescription, "LocalModelingQBI-B3000", 0) == 1:
                    runLocalModelingQBI( 
                                  fileNameDwShell4,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell4,
                                  verbose)

                ################################################################
                # running QBI local modeling for multiple shell
                ################################################################

                outputDirectoryLocalModelingQBIMultipleShell = makeDirectory(
                                         subjectOutputDirectory,
                                         "17-LocalModeling-QBI-Multiple-Shell" )

                if _safe(taskDescription, "LocalModelingQBI-Multiple-Shell", 0) == 1:
                    runLocalModelingQBI( 
                                  fileNameDw,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  verbose )

                ################################################################
                # running NODDI microstructure field
                ################################################################

                outputDirectoryMicrostructureField = makeDirectory(
                    subjectOutputDirectory,
                    "18-NoddiMicrostructureField")

                if _safe(taskDescription, "NoddiMicrostructureField", 0) == 1:
                    runNoddiMicrostructureField(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryMicrostructureField,
                                  verbose )

                ################################################################
                # running SRD tractography
                ################################################################

                outputDirectoryTractographySRD = makeDirectory(
                                                         subjectOutputDirectory,
                                                         "19-Tractography-SRD" )

                if _safe(taskDescription, "TractographySRD", 0) == 1:
                    runTractographySRD( outputDirectoryLocalModelingQBIShell3,
                                        outputDirectoryMaskFromMorphologist,
                                        outputDirectoryTractographySRD,
                                        verbose )

                ################################################################
                # running fiber length histogram with SRD tractogram
                ################################################################

                outputDirectoryFiberLengthHistogramSRD = \
                                  makeDirectory( subjectOutputDirectory,
                                                 "20-FiberLengthHistogram-SRD" )

                if _safe(taskDescription, "FiberLengthHistogramSRD", 0) == 1:
                  runFiberLengthHistogramSRD( 
                                         outputDirectoryTractographySRD,
                                         outputDirectoryFiberLengthHistogramSRD,
                                         verbose )

                ################################################################
                # running long fiber labelling from SRD tractogram
                ################################################################

                outputDirectoryLongFiberLabellingSRD = makeDirectory( \
                                                     subjectOutputDirectory,
                                                     "21-LongFiberLabellingSRD")

                if _safe(taskDescription, "LongFiberLabellingSRD", 0) == 1:
                  runLongFiberLabelling( outputDirectoryTractographySRD,
                                         outputDirectoryMaskFromMorphologist,
                                         outputDirectoryLongFiberLabellingSRD,
                                         verbose )

                ################################################################
                # running short fiber labelling from SRD tractogram
                ################################################################

                outputDirectoryShortFiberLabellingSRD = makeDirectory( \
                                                    subjectOutputDirectory,
                                                    "22-ShortFiberLabellingSRD")

                if _safe(taskDescription, "ShortFiberLabellingSRD", 0) == 1:
                  runShortFiberLabelling( outputDirectoryTractographySRD,
                                          outputDirectoryMaskFromMorphologist,
                                          outputDirectoryShortFiberLabellingSRD,
                                          verbose )
                                           

                ################################################################
                # computing diffusion metrics along long bundles SRD
                ################################################################

                outputDirectoryDiffusionMetricsAlongLongBundlesSRD = \
                  makeDirectory( subjectOutputDirectory,
                                 "23-DiffusionMetricsAlongLongBundlesSRD" )

                if _safe(taskDescription, "DiffusionMetricsAlongLongBundlesSRD", 0) == 1:
                  runDiffusionMetricsAlongBundles( 
                             outputDirectoryLongFiberLabellingSRD,
                             outputDirectoryLocalModelingDTIMultipleShell,
                             outputDirectoryLocalModelingQBIMultipleShell,
                             outputDirectoryMicrostructureField,
                             outputDirectoryMaskFromMorphologist,
                             outputDirectoryDiffusionMetricsAlongLongBundlesSRD,
                             verbose )

                ################################################################
                # computing diffusion metrics along long bundles SRD
                ################################################################

                outputDirectoryDiffusionMetricsAlongCutExtremitiesLongBundlesSRD = \
                  makeDirectory( subjectOutputDirectory,
                                 "23-DiffusionMetricsAlongCutExtremitiesLongBundlesSRD" )

                if ( taskDescription[ 
                   "DiffusionMetricsAlongCutExtremitiesLongBundlesSRD" ] == 1 ):

                  runDiffusionMetricsAlongCutExtremitiesBundles( 
                             outputDirectoryLongFiberLabellingSRD,
                             outputDirectoryLocalModelingDTIMultipleShell,
                             outputDirectoryLocalModelingQBIMultipleShell,
                             outputDirectoryMicrostructureField,
                             outputDirectoryMaskFromMorphologist,
                             outputDirectoryDiffusionMetricsAlongCutExtremitiesLongBundlesSRD,
                             verbose )

                ################################################################
                # computing diffusion metrics along short bundles SRD
                ################################################################

                outputDirectoryDiffusionMetricsAlongShortBundlesSRD = \
                  makeDirectory( subjectOutputDirectory,
                                 "24-DiffusionMetricsAlongShortBundlesSRD" )

                if ( taskDescription[ 
                                "DiffusionMetricsAlongShortBundlesSRD" ] == 1 ):

                  runDiffusionMetricsAlongBundles( 
                            outputDirectoryShortFiberLabellingSRD,
                            outputDirectoryLocalModelingDTIMultipleShell,
                            outputDirectoryLocalModelingQBIMultipleShell,
                            outputDirectoryMicrostructureField,
                            outputDirectoryMaskFromMorphologist,
                            outputDirectoryDiffusionMetricsAlongShortBundlesSRD,
                            verbose )

                ################################################################
                # computing diffusion metrics along short bundles SRD
                ################################################################

                outputDirectoryDiffusionMetricsAlongCutExtremitiesShortBundlesSRD = \
                  makeDirectory( subjectOutputDirectory,
                                 "24-DiffusionMetricsAlongCutExtremitiesShortBundlesSRD" )

                if ( taskDescription[ 
                                "DiffusionMetricsAlongCutExtremitiesShortBundlesSRD" ] == 1 ):

                  runDiffusionMetricsAlongCutExtremitiesBundles( 
                            outputDirectoryShortFiberLabellingSRD,
                            outputDirectoryLocalModelingDTIMultipleShell,
                            outputDirectoryLocalModelingQBIMultipleShell,
                            outputDirectoryMicrostructureField,
                            outputDirectoryMaskFromMorphologist,
                            outputDirectoryDiffusionMetricsAlongCutExtremitiesShortBundlesSRD,
                            verbose )

                ################################################################
                # running freesurfer parcellation
                ################################################################

                outputDirectoryFreeSurferParcellation = makeDirectory(
                                                    subjectOutputDirectory,
                                                    "25-FreeSurferParcellation")

                if ( taskDescription["FreesurferParcellation"] == 1 ):

                    runFreeSurferParcellation(
                                          outputDirectoryMaskFromMorphologist,
                                          subject,
                                          outputDirectoryFreeSurferParcellation,
                                          verbose )

                ################################################################
                # computing diffusion metrics in FreeSurfer ROIs
                ################################################################

                outputDirectoryDiffusionMetricsInROIs = makeDirectory(
                                                   subjectOutputDirectory,
                                                   "26-DiffusionMetricsInROIs" )

                if ( taskDescription[ "DiffusionMetricsInROIs" ] == 1 ):

                  runDiffusionMetricsInROIs( 
                                   outputDirectoryFreeSurferParcellation,
                                   outputDirectoryLocalModelingDTIMultipleShell,
                                   outputDirectoryLocalModelingQBIMultipleShell,
                                   outputDirectoryMicrostructureField,
                                   outputDirectoryMaskFromMorphologist,
                                   outputDirectoryDiffusionMetricsInROIs,
                                   verbose )

                ################################################################
                # running fast segmentation
                ################################################################

                outputDirectoryFastSegmentation = makeDirectory(
                                                         subjectOutputDirectory,
                                                         "27-FastSegmentation")

                if (taskDescription["FastSegmentation"] == 1):
 
                  runFASTSegmentation( outputDirectoryMaskFromMorphologist,
                                       outputDirectoryFastSegmentation,
                                       verbose )

                ################################################################
                # computing diffusion metrics in white and grey matter
                ################################################################

                outputDirectoryDiffusionMetricsInWhiteGreyMatter = \
                  makeDirectory( subjectOutputDirectory,
                                 "28-DiffusionMetricsInWhiteGreyMatter" )

                if ( taskDescription[ 
                                   "DiffusionMetricsInWhiteGreyMatter" ] == 1 ):

                  runDiffusionMetricsInWhiteGreyMatter( 
                               outputDirectoryFastSegmentation,
                               outputDirectoryLocalModelingDTIMultipleShell,
                               outputDirectoryLocalModelingQBIMultipleShell,
                               outputDirectoryMicrostructureField,
                               outputDirectoryMaskFromMorphologist,
                               outputDirectoryDiffusionMetricsInWhiteGreyMatter,
                               verbose )

              ##################################################################
              # computing diffusion metrics in FreeSurfer ROIs
              ##################################################################

                outputDirectoryDiffusionMetricsInHippROIs = makeDirectory(
                                                subjectOutputDirectory,
                                                "29-DiffusionMetricsInHippROIs")

                if (taskDescription["DiffusionMetricsInHippROIs"] == 1):

                    runDiffusionMetricsInHippROIs(
                                 outputDirectoryFreeSurferParcellation,
                                 outputDirectoryLocalModelingDTIMultipleShell,
                                 outputDirectoryLocalModelingQBIMultipleShell,
                                 outputDirectoryMicrostructureField,
                                 outputDirectoryMaskFromMorphologist,
                                 outputDirectoryDiffusionMetricsInHippROIs,
                                 verbose )

              ##################################################################
              # normalization
              ##################################################################

                outputDirectoryNormalization = makeDirectory(
                                                         subjectOutputDirectory,
                                                         "30-Normalization")

                templateDirectory = "/work/templates/mni_icbm152_nlin_asym_09a"

                if (taskDescription["Normalization"] == 1):

                    runNormalization( outputDirectoryMaskFromMorphologist,
                                      templateDirectory,
                                      outputDirectoryNormalization,
                                      verbose)

              ##################################################################
              # connectivity matrix
              ##################################################################

                # outputDirectoryConnectivityMatrix = makeDirectory(
                #                                         subjectOutputDirectory,
                #                                         "31-ConnectivityMatrix")

                # if ( session == 'V1' ):

                #   subjectV1ConnectivityMatrixDirectories.append( 
                #                              outputDirectoryConnectivityMatrix )

                # elif ( session == 'V2' ):

                #   subjectV2ConnectivityMatrixDirectories.append( 
                #                              outputDirectoryConnectivityMatrix )

                # else:

                #   subjectV3ConnectivityMatrixDirectories.append( 
                #                              outputDirectoryConnectivityMatrix )

                # if (taskDescription["ConnectivityMatrix"] == 1):

                #     runConnectivityMatrix( 
                #                           outputDirectoryTractographySRD,
                #                           outputDirectoryMaskFromMorphologist,
                #                           outputDirectoryFreeSurferParcellation,
                #                           outputDirectoryNormalization,
                #                           outputDirectoryConnectivityMatrix,
                #                           verbose)

    ############################################################################
    # building roi-to-roi connectivity template 
    ############################################################################

    outputDirectoryFullConnectivityTemplate = makeDirectory( 
                                                 outputDirectory,
                                                 "00-FullConnectivityTemplate" )

    if ( taskDescription["FullConnectivityTemplate"] == 1 ):

      runFullConnectivityTemplate( subjectV1ConnectivityMatrixDirectories,
                                   subjectV2ConnectivityMatrixDirectories,
                                   subjectV3ConnectivityMatrixDirectories,
                                   outputDirectoryFullConnectivityTemplate,
                                   verbose )

    ############################################################################
    # second loop over groups and individuals to compute diffusion metrics in 
    # hippocampi connectivity template
    ############################################################################

    for group in subjects.keys():

        groupOutputDirectory = os.path.join(outputDirectory, str( group ) )

        for subject in subjects[group]:

            subjectOutputDirectoryTemp = os.path.join(groupOutputDirectory,
                                                      str(subject))

            for session in session.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      session)

                if (verbose == True):
                    print("===================================================")
                    print(group + " / " + subject)
                    print("===================================================")

                outputDirectoryLocalModelingDTIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '13-LocalModeling-DTI-Multiple-Shell' )

                outputDirectoryLocalModelingQBIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '17-LocalModeling-QBI-Multiple-Shell' )

                outputDirectoryMicrostructureField = os.path.join( 
                                            subjectOutputDirectory,
                                            '18-NoddiMicrostructureField' )

                outputDirectoryMaskFromMorphologist = os.path.join( 
                                            subjectOutputDirectory,
                                            '07-MaskFromMorphologistPipeline' )

                outputDirectoryNormalization = os.path.join( subjectOutputDirectory,
                                                             '30-Normalization' )

                if ( taskDescription[ "DiffusionMetricsInHippocampiConnectivityTemplate" ] == 1 ):

                  outputDirectoryDiffusionMetricsInHippocampiConnectivityTemplate = makeDirectory(
                                               subjectOutputDirectory,
                                               "32-DiffusionMetricsInHippocampiConnectivityTemplate" )

                  runDiffusionMetricsInHippocampiConnectivityTemplate( 
                                  outputDirectoryFullConnectivityTemplate,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInHippocampiConnectivityTemplate,
                                  verbose )

    ############################################################################
    # second loop over groups and individuals to compute diffusion metrics in 
    # full connectivity template
    ############################################################################

    for group in subjects.keys():

        groupOutputDirectory = os.path.join(outputDirectory, str( group ) )

        for subject in subjects[group]:

            subjectOutputDirectoryTemp = os.path.join(groupOutputDirectory,
                                                      str(subject))

            for session in session.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      session)

                if (verbose == True):
                    print("===================================================")
                    print(group + " / " + subject)
                    print("===================================================")

                outputDirectoryLocalModelingDTIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '13-LocalModeling-DTI-Multiple-Shell' )

                outputDirectoryLocalModelingQBIMultipleShell = os.path.join( 
                                            subjectOutputDirectory,
                                            '17-LocalModeling-QBI-Multiple-Shell' )

                outputDirectoryMicrostructureField = os.path.join( 
                                            subjectOutputDirectory,
                                            '18-NoddiMicrostructureField' )

                outputDirectoryMaskFromMorphologist = os.path.join( 
                                            subjectOutputDirectory,
                                            '07-MaskFromMorphologistPipeline' )

                outputDirectoryNormalization = os.path.join( subjectOutputDirectory,
                                                             '30-Normalization' )

                outputDirectoryConnectivityMatrix = os.path.join( subjectOutputDirectory,
                                                             '31-ConnectivityMatrix' )

                if ( taskDescription[ "DiffusionMetricsInFullConnectivityTemplate" ] == 1 ):

                  outputDirectoryDiffusionMetricsInFullConnectivityTemplate = makeDirectory(
                                               subjectOutputDirectory,
                                               "33-DiffusionMetricsInFullConnectivityTemplate" )

                  runDiffusionMetricsInFullConnectivityTemplate( 
                                  outputDirectoryFullConnectivityTemplate,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInFullConnectivityTemplate,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInConnectivityMatrix" ] == 1 ):

                  outputDirectoryDiffusionMetricsInConnectivityMatrix = makeDirectory(
                                               subjectOutputDirectory,
                                               "34-DiffusionMetricsInConnectivityMatrix" )

                  runDiffusionMetricsInConnectivityMatrix( 
                                  outputDirectoryConnectivityMatrix,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryDiffusionMetricsInConnectivityMatrix,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInMNISpace" ] == 1 ):

                  outputDirectoryDiffusionMetricsInMNISpace = makeDirectory(
                                               subjectOutputDirectory,
                                               "35-DiffusionMetricsInMNISpace" )

                  runDiffusionMetricsInMNISpace(
                                  templateDirectory, 
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryNormalization,
                                  outputDirectoryDiffusionMetricsInMNISpace,
                                  verbose )

                if ( taskDescription[ "DiffusionMetricsInCutExtremitiesConnectivityMatrix" ] == 1 ):

                  outputDirectoryDiffusionMetricsInCutExtremitiesConnectivityMatrix = makeDirectory(
                                               subjectOutputDirectory,
                                               "36-DiffusionMetricsInCutExtremitiesConnectivityMatrix" )

                  runDiffusionMetricsInConnectivityMatrix( 
                                  outputDirectoryConnectivityMatrix,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  outputDirectoryLocalModelingQBIMultipleShell,
                                  outputDirectoryMicrostructureField,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryDiffusionMetricsInCutExtremitiesConnectivityMatrix,
                                  verbose )

