import os
import json
import sys
import shutil
sys.path.insert(0, os.path.join(os.sep, 'usr', 'share', 'gkg', 'python'))
import gkg
from CopyFileDirectoryRm import *

def runNoddiMicrostructureField(subjectDirectoryEddyCurrentCorrection,
                                 subjectDirectoryMorphologist,
                                 outputDirectory,
                                 verbose):

    if verbose:
        print("NODDI MICROSTRUCTURE FIELD")
        print("-------------------------------------------------------------")

    def all_files_exist(file_paths):
        return all(os.path.exists(file_path) for file_path in file_paths)

    def execute_command(command):
        output_files = command['parameters']['outputFileNames']
        if not all_files_exist(output_files):
            gkg.executeCommand(command)

    fileNameIntracellularFraction = os.path.join(outputDirectory,
                                                  'intracellular_fraction')

    fileNameIsotropicDiffusivity = os.path.join(outputDirectory,
                                                 'isotropic_diffusivity')

    fileNameIsotropicFraction = os.path.join(outputDirectory,
                                              'isotropic_fraction')

    fileNameKappa = os.path.join(outputDirectory, 'kappa')

    fileNameStationaryFraction = os.path.join(outputDirectory,
                                              'stationary_fraction')

    fileNameParallelDiffusivity = os.path.join(outputDirectory,
                                                'parallel_diffusivity')

    fileNameOrientationDispersion = os.path.join(outputDirectory,
                                                  'orientation_dispersion')

    fileNameT2 = os.path.join(subjectDirectoryEddyCurrentCorrection,
                               't2_wo_eddy_current.ima')
    fileNameDw = os.path.join(subjectDirectoryEddyCurrentCorrection,
                               'dw_wo_eddy_current.ima')
    fileNameMask = os.path.join(subjectDirectoryMorphologist,
                                 'mask.ima')

    # Check if any of the output files exist, and execute the command only if any are missing
    execute_command(
        {'algorithm': 'DwiMicrostructureField',
         'parameters': \
             {'fileNameT2': str(fileNameT2),
              'fileNameDW': str(fileNameDw),
              'fileNameMask': str(fileNameMask),
              'modelType': 'noddi_microstructure_cartesian_field',
              'odfFunctorNames': ('intracellular_fraction',
                                  'isotropic_diffusivity',
                                  'isotropic_fraction',
                                  'kappa',
                                  'stationary_fraction',
                                  'parallel_diffusivity',
                                  'orientation_dispersion'),
              'outputFileNames': (str(fileNameIntracellularFraction),
                                  str(fileNameIsotropicDiffusivity),
                                  str(fileNameIsotropicFraction),
                                  str(fileNameKappa),
                                  str(fileNameStationaryFraction),
                                  str(fileNameParallelDiffusivity),
                                  str(fileNameOrientationDispersion)),
              'outputOrientationCount': 60,
              'radius': 4.0,  # 3
              'thresholdRatio': 0.04,
              'volumeFormat': 'gis',
              'meshMapFormat': 'aimsmesh',
              'textureMapFormat': 'aimsmesh',
              'rgbScale': 1.0,
              'meshScale': 1.0,
              'lowerFAThreshold': 0.0,
              'upperFAThreshold': 0.1,
              'specificStringParameters': 'watson',
              'specificScalarParameters': (0.0, 0.5, 0.0, 1.7e-9, 3.0e-9, 0.0,
                                           0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
                                           1.0, 1.0, 100, 3.0e-9, 4.0e-9, 1.0,
                                           0.1, 0.1, 1.0, 0.2e-9, 0.2e-9, 0.1,
                                           0, 0, 0, 0, 1, 1, 0,
                                           0.02,  # noise std / signal mean
                                           1, 5,  # quicksearch
                                           1, 1000, 0.001,  # NLP
                                           0, 500, 100, 50, 10000),  # MCMC
              'ascii': False,
              'verbose': verbose
              },
         'verbose': verbose
         }
    )

 
    if not file_exists([fileNameOrientationDispersion + '.ima']):
        # Convert orientation_dispersion.ima to ODI.nii
        gkg.executeCommand(
            {'algorithm': 'GkgExecuteCommand',
             'parameters': {'command': 'Gis2NiftiConverter',
                            'arguments': ['-i', 'orientation_dispersion.ima', '-o', 'ODI.nii', '-verbose'],
                            'workingDirectory': outputDirectory},
             'verbose': verbose}
        )

    if verbose:
        print("-------------------------------------------------------------")

