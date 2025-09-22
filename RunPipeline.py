import os, json, sys, shutil

sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
from core.command.CommandFactory import *

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

from CopyFileDirectoryRm import *
from DicomConversion import *
from GisConversion import *
from NiftiConversion import *
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


def runPipeline(inputDicomDirectory, subjectJsonFileName, taskJsonFileName, timePoint, outputDirectory, verbose):
    ##############################################################################
    # reading subject information
    ##############################################################################
    if not os.path.isdir(outputDirectory):
        os.makedirs(outputDirectory, exist_ok=True)

    subjects = dict()
    with open(subjectJsonFileName, 'r') as f:

        subjects = json.load(f)

    ##############################################################################
    # reading task information
    ##############################################################################

    taskDescription = dict()
    with open(taskJsonFileName, 'r') as f:

        taskDescription = json.load(f)

    ##############################################################################
    # first loop over groups and individuals to perform individual processing
    ##############################################################################

    subjectV1ConnectivityMatrixDirectories = []
    subjectV2ConnectivityMatrixDirectories = []
    subjectV3ConnectivityMatrixDirectories = []

    for group in subjects.keys():

        for subject in subjects[group]:

            for timepoint in timePoint.split(','):

                if (verbose == True):
                    print("===================================================")
                    print(group + " / " + subject)
                    print("===================================================")

                ################################################################
                # reading description json files
                ################################################################

                subjectRawDataDirectory = os.path.join(inputDicomDirectory, group,
                                                       subject, timepoint, '01-RawData')

                if not os.path.isdir(subjectRawDataDirectory):
                    continue

                subjectFileNameJson = os.path.join(subjectRawDataDirectory,
                                                   'description.json')
                description = dict()
                with open(subjectFileNameJson, 'r') as f:

                    description = json.load(f)

                if (verbose == True):

                    for series in sorted(description.keys()):
                        print(series + " -> " + description[series])

                    print("---------------------------------------------------")

                groupOutputDirectory = makeDirectory(outputDirectory, str(group))
                subjectOutputDirectoryTemp = makeDirectory(groupOutputDirectory,
                                                       str(subject))

                subjectOutputDirectory = makeDirectory(subjectOutputDirectoryTemp,
                                                       timepoint)

                if not os.path.isdir(subjectOutputDirectory):
                    os.makedirs(subjectOutputDirectory, exist_ok=True)

                ################################################################
                # running DICOM copy
                ################################################################

                outputDirectoryDicomCopy = makeDirectory(subjectOutputDirectory,
                                                         "01-DicomCopy")

                if (taskDescription["DicomCopy"] == 1):
                    runDicomConversion(subjectRawDataDirectory,
                                       description,
                                       outputDirectoryDicomCopy,
                                       verbose)

                ################################################################
                # running GIS conversion
                ################################################################

                outputDirectoryGisConversion = makeDirectory(subjectOutputDirectory,
                                                             "02-GisConversion")

                if ( subjects[group][subject] ):
                  differentMatrixSequences = subjects[group][subject]['differentMatrixSequences']

                if (taskDescription["GisConversion"] == 1):
                    runGisConversion(subjectRawDataDirectory,
                                     description,
                                     differentMatrixSequences,
                                     timePoint,
                                     outputDirectoryGisConversion,
                                     verbose)

                ##########################################################################
                # running Nifti conversion
                ##########################################################################

                outputDirectoryNiftiConversion = makeDirectory(subjectOutputDirectory,
                                                               "03-NiftiConversion")

                if (taskDescription["NiftiConversion"] == 1):
                    runNiftiConversion(outputDirectoryGisConversion,
                                       description,
                                       outputDirectoryNiftiConversion,
                                       verbose)

                ##########################################################################
                # running susceptibility artefact correction from top up
                ##########################################################################

                outputDirectoryTopUpCorrection = makeDirectory(subjectOutputDirectory,
                                                               "04-TopUpCorrection")

                if ( subjects[group][subject] ):
                  differentTopUpAcquisitions = subjects[group][subject]['differentTopUpAcquisitions']


                if (taskDescription["TopUpCorrection"] == 1):
                    runTopUpCorrection(outputDirectoryNiftiConversion,
                                       description,
                                       differentTopUpAcquisitions,
                                       timePoint,
                                       outputDirectoryTopUpCorrection,
                                       verbose)

                ##########################################################################
                # running orientation and b-value file decoding
                ##########################################################################

                outputDirectoryOrientationAndBValueFileDecoding = \
                    makeDirectory(subjectOutputDirectory,
                                  "05-OrientationAndBValueFileDecoding")

                flippingTypes = ['y']

                if (taskDescription["OrientationAndBValueFileDecoding"] == 1):
                    runOrientationAndBValueFileDecoding(
                        outputDirectoryGisConversion,
                        outputDirectoryTopUpCorrection,
                        flippingTypes,
                        description,
                        outputDirectoryOrientationAndBValueFileDecoding,
                        verbose)

                ##########################################################################
                # running q-space sampling addition
                ##########################################################################

                outputDirectoryQSpaceSamplingAddition = makeDirectory( \
                    subjectOutputDirectory,
                    "06-QSpaceSamplingAddition")

                if (taskDescription["QSpaceSamplingAddition"] == 1):
                    runQSpaceSamplingAddition(
                        outputDirectoryOrientationAndBValueFileDecoding,
                        outputDirectoryQSpaceSamplingAddition,
                        verbose)

                ##########################################################################
                # running mask from Morphologist
                ##########################################################################

                outputDirectoryMaskFromMorphologist = makeDirectory( \
                    subjectOutputDirectory,
                    "07-MaskFromMorphologistPipeline")

                fileNameT1APC = os.path.join(outputDirectoryGisConversion, 't1.APC')

                ### BEGIN - Copy old data ###
                # outputDirectorybak = outputDirectory + '.bak'
                # groupOutputDirectorybak = os.path.join(outputDirectorybak, str(group))
                # subjectOutputDirectorybak = os.path.join(groupOutputDirectorybak,
                #                                       str(subject),
                #                                       timepoint)
                # outputDirectoryGisConversionbak = os.path.join(subjectOutputDirectorybak, "02-GisConversion")
                # fileNameT1APCbak = os.path.join(outputDirectoryGisConversionbak, 't1.APC')
                # if os.path.isfile(fileNameT1APCbak):
                #     shutil.copy(fileNameT1APCbak, outputDirectoryGisConversion)
                # else:
                #     print(f'File not found: {fileNameT1APCbak}')
                ### END - Copy old data ###

                if (taskDescription["Morphologist"] == 1):
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
                    "08-OutlierCorrection")

                if (taskDescription["OutlierCorrection"] == 1):
                    runOutlierCorrection(outputDirectoryQSpaceSamplingAddition,
                                         outputDirectoryMaskFromMorphologist,
                                         outputDirectoryOutlierCorrection,
                                         verbose)

                ##########################################################################
                # running eddy current and motion correction
                ##########################################################################

                outputDirectoryEddyCurrentAndMotionCorrection = makeDirectory( \
                    subjectOutputDirectory,
                    "09-EddyCurrentAndMotionCorrection")

                if (taskDescription["EddyCurrentCorrection"] == 1):
                    runEddyCurrentAndMotionCorrection(
                        outputDirectoryOutlierCorrection,
                        outputDirectoryMaskFromMorphologist,
                        outputDirectoryEddyCurrentAndMotionCorrection,
                        verbose)

                ##########################################################################
                # running DTI local modeling for b=300s/mm2
                ##########################################################################

                outputDirectoryLocalModelingDTIShell1 = makeDirectory(
                    subjectOutputDirectory,
                    "10-LocalModeling-DTI-B0200")
                fileNameDwShell1 = os.path.join(
                    outputDirectoryEddyCurrentAndMotionCorrection,
                    "dw_shell1.ima")

                if (taskDescription["LocalModelingDTI-B0200"] == 1):
                    runLocalModelingDTI(fileNameDwShell1,
                                        outputDirectoryEddyCurrentAndMotionCorrection,
                                        outputDirectoryMaskFromMorphologist,
                                        outputDirectoryLocalModelingDTIShell1,
                                        verbose)

                ##########################################################################
                # running DTI local modeling for b=1200s/mm2
                ##########################################################################

                outputDirectoryLocalModelingDTIShell2 = makeDirectory(
                    subjectOutputDirectory,
                    "11-LocalModeling-DTI-B1500")
                fileNameDwShell2 = os.path.join(
                    outputDirectoryEddyCurrentAndMotionCorrection,
                    "dw_shell2.ima")

                if (taskDescription["LocalModelingDTI-B1500"] == 1):
                    runLocalModelingDTI(fileNameDwShell2,
                                        outputDirectoryEddyCurrentAndMotionCorrection,
                                        outputDirectoryMaskFromMorphologist,
                                        outputDirectoryLocalModelingDTIShell2,
                                        verbose)

                ################################################################
                # running DTI local modeling for b=2700s/mm2
                ################################################################

                outputDirectoryLocalModelingDTIShell3 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "12-LocalModeling-DTI-B2500" )
                fileNameDwShell3 = os.path.join(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  "dw_shell3.ima")

                if ( taskDescription[ "LocalModelingDTI-B2500" ] == 1 ):

                    runLocalModelingDTI(
                                  fileNameDwShell3,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingDTIShell3,
                                  verbose )


                ################################################################
                # running DTI local modeling
                ################################################################

                outputDirectoryLocalModelingDTIMultipleShell = makeDirectory(
                                         subjectOutputDirectory,
                                         "13-LocalModeling-DTI-Multiple-Shell" )

                fileNameDw = os.path.join(
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  "dw_wo_eddy_current.ima")

                if ( taskDescription[ 
                                     "LocalModelingDTI-Multiple-Shell" ] == 1 ):

                    runLocalModelingDTI( 
                                  fileNameDw,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingDTIMultipleShell,
                                  verbose )


                ################################################################
                # running QBI local modeling for b=200s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell1 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "14-LocalModeling-QBI-B0200" )

                if ( taskDescription[ "LocalModelingQBI-B0200" ] == 1 ):

                  runLocalModelingQBI( 
                                  fileNameDwShell1,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell1,
                                  verbose )


                ################################################################
                # running QBI local modeling for b=1200s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell2 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "15-LocalModeling-QBI-B1500" )

                if ( taskDescription[ "LocalModelingQBI-B1500" ] == 1 ):

                  runLocalModelingQBI( 
                                  fileNameDwShell2,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell2,
                                  verbose )


                ################################################################
                # running QBI local modeling for b=2700s/mm2
                ################################################################

                outputDirectoryLocalModelingQBIShell3 = makeDirectory(
                                                  subjectOutputDirectory,
                                                  "16-LocalModeling-QBI-B2500" )

                if ( taskDescription[ "LocalModelingQBI-B2500" ] == 1 ):

                    runLocalModelingQBI( 
                                  fileNameDwShell3,
                                  outputDirectoryEddyCurrentAndMotionCorrection,
                                  outputDirectoryMaskFromMorphologist,
                                  outputDirectoryLocalModelingQBIShell3,
                                  verbose)


                ################################################################
                # running QBI local modeling for multiple shell
                ################################################################

                outputDirectoryLocalModelingQBIMultipleShell = makeDirectory(
                                         subjectOutputDirectory,
                                         "17-LocalModeling-QBI-Multiple-Shell" )

                if ( taskDescription[ 
                                     "LocalModelingQBI-Multiple-Shell" ] == 1 ):

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

                if ( taskDescription[ "NoddiMicrostructureField" ] == 1 ):

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

                if ( taskDescription[ "TractographySRD" ] == 1 ):

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

                if ( taskDescription[ "FiberLengthHistogramSRD" ] == 1 ):

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

                if ( taskDescription["LongFiberLabellingSRD"] == 1 ):

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

                if ( taskDescription["ShortFiberLabellingSRD"] == 1 ):

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

                if ( taskDescription[ 
                                 "DiffusionMetricsAlongLongBundlesSRD" ] == 1 ):

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

                templateDirectory = '/mnt/POOL_IRM06/CONHECT/mni_icbm152_nlin_asym_09a_nifti/mni_icbm152_nlin_asym_09a'

                if (taskDescription["Normalization"] == 1):

                    runNormalization( outputDirectoryMaskFromMorphologist,
                                      templateDirectory,
                                      outputDirectoryNormalization,
                                      verbose)

              ##################################################################
              # connectivity matrix
              ##################################################################

                outputDirectoryConnectivityMatrix = makeDirectory(
                                                        subjectOutputDirectory,
                                                        "31-ConnectivityMatrix")

                if ( timepoint == 'V1' ):

                  subjectV1ConnectivityMatrixDirectories.append( 
                                             outputDirectoryConnectivityMatrix )

                elif ( timepoint == 'V2' ):

                  subjectV2ConnectivityMatrixDirectories.append( 
                                             outputDirectoryConnectivityMatrix )

                else:

                  subjectV3ConnectivityMatrixDirectories.append( 
                                             outputDirectoryConnectivityMatrix )

                if (taskDescription["ConnectivityMatrix"] == 1):

                    runConnectivityMatrix( 
                                          outputDirectoryTractographySRD,
                                          outputDirectoryMaskFromMorphologist,
                                          outputDirectoryFreeSurferParcellation,
                                          outputDirectoryNormalization,
                                          outputDirectoryConnectivityMatrix,
                                          verbose)


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

            for timepoint in timePoint.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      timepoint)

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

            for timepoint in timePoint.split(','):

                subjectOutputDirectory = os.path.join(subjectOutputDirectoryTemp,
                                                      timepoint)

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
