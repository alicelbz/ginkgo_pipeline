import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runDiffusionMetricsInMNISpace( templateDirectory,
                                   subjectDirectoryLocalModelingDTI,
                                   subjectDirectoryLocalModelingQBI,
                                   subjectDirectoryNoddiMicrostructureField,
                                   subjectDirectoryMaskFromMorphologist,
                                   subjectDirectoryNormalization,
                                   outputDirectory,
                                   verbose ):
                      
  
  if ( verbose == True ):
  
    print( "COMPUTING DIFFUSION METRICS IN MNI SPACE " )
    print( "-------------------------------------------------------------" )


  fileNameAtlasT1 = os.path.join( templateDirectory, 
                                  'mni_icbm152_t1_tal_nlin_asym_09a_masked.ima' )

  fileNameDwToAtlasTransform = os.path.join( subjectDirectoryNormalization,
                                          'dw-to-atlas.trm' )

  fileNameDirectTransform = os.path.join( subjectDirectoryNormalization,
                                          't1-to-atlas.ima' )

  fileNameInverseTransform = os.path.join( subjectDirectoryNormalization,
                                           'atlas-to-t1.ima' )


  ##############################################################################
  # GFA
  ##############################################################################

  fileNameGFA = os.path.join( subjectDirectoryLocalModelingQBI, "aqbi_gfa.ima" )
  fileNameGFAInMNISpace = os.path.join( outputDirectory, "aqbi_gfa_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameGFA ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameGFAInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameGFAInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "aqbi_gfa_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameGFAInMNISpace ),
          'fileNameOut' : str( fileNameGFAInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # FA
  ##############################################################################

  fileNameFA = os.path.join( subjectDirectoryLocalModelingDTI, "dti_fa.ima" )
  fileNameFAInMNISpace = os.path.join( outputDirectory, "dti_fa_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameFA ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameFAInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameFAInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "dti_fa_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameFAInMNISpace ),
          'fileNameOut' : str( fileNameFAInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # MD
  ##############################################################################

  fileNameMD = os.path.join( subjectDirectoryLocalModelingDTI, "dti_adc.ima" )

  fileNameMDInMNISpace = os.path.join( outputDirectory, "dti_adc_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameMD ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameMDInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameMDInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "dti_adc_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameMDInMNISpace ),
          'fileNameOut' : str( fileNameMDInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # PARALLEL DIFFUSIVITY
  ##############################################################################

  fileNameAD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_parallel_diffusivity.ima" )
  fileNameADInMNISpace = os.path.join( outputDirectory, "dti_parallel_diffusivity_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameAD ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameADInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameADInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "dti_parallel_diffusivity_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameADInMNISpace ),
          'fileNameOut' : str( fileNameADInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )

  ##############################################################################
  # TRANSVERSE DIFFUSIVITY
  ##############################################################################

  fileNameRD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_transverse_diffusivity.ima" )
  fileNameRDInMNISpace = os.path.join( outputDirectory, "dti_transverse_diffusivity_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameRD ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameRDInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameRDInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "dti_transverse_diffusivity_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameRDInMNISpace ),
          'fileNameOut' : str( fileNameRDInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # INTRACELLULAR FRACTION
  ##############################################################################

  fileNameFIntra = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                                 "intracellular_fraction.ima" )
  fileNameFIntraInMNISpace = os.path.join( outputDirectory, 
                                           "intracellular_fraction_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameFIntra ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameFIntraInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameFIntraInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "intracellular_fraction_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameFIntraInMNISpace ),
          'fileNameOut' : str( fileNameFIntraInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # ORIENTATION DISPERSION INDEX
  ##############################################################################

  fileNameODI = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                              "orientation_dispersion.ima" )
  fileNameODIInMNISpace = os.path.join( outputDirectory, 
                                        "orientation_dispersion_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameODI ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameODIInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameODIInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "orientation_dispersion_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameODIInMNISpace ),
          'fileNameOut' : str( fileNameODIInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # ISOTROPIC FRACTION
  ##############################################################################

  fileNameFISO = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "isotropic_fraction.ima" )
  fileNameFISOInMNISpace = os.path.join( outputDirectory, 
                                        "isotropic_fraction_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameFISO ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameFISOInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameFISOInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "isotropic_fraction_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameFISOInMNISpace ),
          'fileNameOut' : str( fileNameFISOInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )


  ##############################################################################
  # STATIONARY FRACTION
  ##############################################################################

  fileNameFSTAT = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "stationary_fraction.ima" )
  fileNameFSTATInMNISpace = os.path.join( outputDirectory, 
                                        "stationary_fraction_in_mni_space.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameFSTAT ),
          'fileNameTemplate' : str( fileNameAtlasT1 ),
          'fileNameTransforms' : ( fileNameDwToAtlasTransform, 
                                   fileNameDirectTransform, 
                                   fileNameInverseTransform ),
          'fileNameOut' : str( fileNameFSTATInMNISpace ),
          'order' : 3,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameFSTATInMNISpaceNifti = os.path.join( outputDirectory, 
                                             "stationary_fraction_in_mni_space.nii" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameFSTATInMNISpace ),
          'fileNameOut' : str( fileNameFSTATInMNISpaceNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )

