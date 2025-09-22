import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runDiffusionMetricsInROIs( subjectDirectoryFreeSurferParcellation,
                               subjectDirectoryLocalModelingDTI,
                               subjectDirectoryLocalModelingQBI,
                               subjectDirectoryNoddiMicrostructureField,
                               subjectDirectoryMaskFromMorphologist,
                               outputDirectory,
                               verbose ):
                      
  
  if ( verbose == True ):
  
    print( "COMPUTING DIFFUSION METRICS IN FREESURFER ROIs" )
    print( "-------------------------------------------------------------" )

  fileNameFreeSurferROIs = os.path.join( subjectDirectoryFreeSurferParcellation,
                                         '05-ToNativeSpace',
                                         'wmparc.ima' )

  fileNameFreeSurferROIsS16 = os.path.join( outputDirectory, 'wmparc-S16.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Combiner',
      'parameters' : \
        { 'fileNameIns' : str( fileNameFreeSurferROIs ),
          'fileNameOut' : str( fileNameFreeSurferROIsS16 ),
          'functor1s' : 'id',
          'functor2s' : 'id',
          'numerator1s' : ( 1.0, 1.0 ),
          'denominator1s' : ( 1.0, 1.0 ),
          'numerator2s' : 1.0,
          'denominator2s' : 1.0,
          'operators' : '*',
          'fileNameMask' : '',
          'mode' : 'gt',
          'threshold1' : 0.0,
          'threshold2' : 0.0,
          'background' : 0.0,
          'outputType' : 'int16_t',
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameT1ToDwTransform3d = os.path.join( subjectDirectoryMaskFromMorphologist,
                                            't1-to-dw.trm' )

  fileNameFreeSurferROIsInT2Space = os.path.join( outputDirectory, 
                                                  'wmparc-in-t2-space.ima' )

  fileNameGFA = os.path.join( subjectDirectoryLocalModelingQBI, "aqbi_gfa.ima" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameFreeSurferROIsS16 ),
          'fileNameTemplate' : str( fileNameGFA ),
          'fileNameTransforms' : str( fileNameT1ToDwTransform3d ),
          'fileNameOut' : str( fileNameFreeSurferROIsInT2Space ),
          'order' : 0,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  ##############################################################################
  # GFA
  ##############################################################################

  fileNameGFA = os.path.join( subjectDirectoryLocalModelingQBI, "aqbi_gfa.ima" )
  fileNameGFASpreadsheet = os.path.join( outputDirectory, "aqbi_gfa" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameGFA + \
            ' -f csv --verbose > ' + fileNameGFASpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # FA
  ##############################################################################

  fileNameFA = os.path.join( subjectDirectoryLocalModelingDTI, "dti_fa.ima" )
  fileNameFASpreadsheet = os.path.join( outputDirectory, "dti_fa" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameFA + \
            ' -f csv --verbose > ' + fileNameFASpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # MD
  ##############################################################################

  fileNameMD = os.path.join( subjectDirectoryLocalModelingDTI, "dti_adc.ima" )
  fileNameMDSpreadsheet = os.path.join( outputDirectory, "dti_adc" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameMD + \
            ' -f csv --verbose > ' + fileNameMDSpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # PARALLEL DIFFUSIVITY
  ##############################################################################

  fileNameAD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_parallel_diffusivity.ima" )
  fileNameADSpreadsheet = os.path.join( outputDirectory, 
                                        "dti_parallel_diffusivity" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameAD + \
            ' -f csv --verbose > ' + fileNameADSpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # TRANSVERSE DIFFUSIVITY
  ##############################################################################

  fileNameRD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_transverse_diffusivity.ima" )
  fileNameRDSpreadsheet = os.path.join( outputDirectory, 
                                        "dti_transverse_diffusivity" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameRD + \
            ' -f csv --verbose > ' + fileNameRDSpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # INTRACELLULAR FRACTION
  ##############################################################################

  fileNameFIntra = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                                 "intracellular_fraction.ima" )
  fileNameFIntraSpreadsheet = os.path.join( outputDirectory, 
                                            "intracellular_fraction" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameFIntra + \
            ' -f csv --verbose > ' + fileNameFIntraSpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # ORIENTATION DISPERSION INDEX
  ##############################################################################

  fileNameODI = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                              "orientation_dispersion.ima" )
  fileNameODISpreadsheet = os.path.join( outputDirectory, "odi" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameODI + \
            ' -f csv --verbose > ' + fileNameODISpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # ISOTROPIC FRACTION
  ##############################################################################

  fileNameFISO = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "isotropic_fraction.ima" )
  fileNameFISOSpreadsheet = os.path.join( outputDirectory, 
                                          "isotropic_fraction" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameFISO + \
            ' -f csv --verbose > ' + fileNameFISOSpreadsheet + '.csv'
  os.system( command )


  ##############################################################################
  # STATIONARY FRACTION
  ##############################################################################

  fileNameFSTAT = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "stationary_fraction.ima" )
  fileNameSTATSpreadsheet = os.path.join( outputDirectory, 
                                          "stationary_fraction" )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameFreeSurferROIsInT2Space + \
            ' -s ' + fileNameFSTAT + \
            ' -f csv --verbose > ' + fileNameSTATSpreadsheet + '.csv'
  os.system( command )
