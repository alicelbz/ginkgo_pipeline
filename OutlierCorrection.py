import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runOutlierCorrection( subjectDirectoryQSpaceSamplingAddition,
                          subjectDirectoryMaskFromMorphologist,
                          outputDirectory,
                          verbose ):
                      
  
  if ( verbose == True ):
  
    print( "OUTLIER CORRECTION" )
    print( "-------------------------------------------------------------" )
  

  fileNameT2 = os.path.join( subjectDirectoryQSpaceSamplingAddition, "t2.ima" )

  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist, 
                               'mask.ima' )

  fileNameDwShell1 = os.path.join( subjectDirectoryQSpaceSamplingAddition, 
                                   "dw_shell1.ima" )
  fileNameDwShell1Outliers = os.path.join( outputDirectory, 
                                           "dw_shell1_wo_outlier.ima" )
  fileNameShell1Outliers = os.path.join( outputDirectory, "shell1_outlier.py" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiOutlierFilter',
      'parameters' : \
        { 'fileNameT2' : str( fileNameT2 ),
          'fileNameDW' : str( fileNameDwShell1 ),
          'fileNameMask' : str( fileNameMask ),
          'sliceAxis' : 'z',
          'fileNameCorrectedDW' : str( fileNameDwShell1Outliers ),
          'fileNameOutliers' : str( fileNameShell1Outliers ),
          'outlierFactor' : 3.0,
          'radius' : 3.6,
          'thresholdRatio' : 0.04,
          'volumeFormat' : 'gis',
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameDwShell2 = os.path.join( subjectDirectoryQSpaceSamplingAddition, 
                                   "dw_shell2.ima" )
  fileNameDwShell2Outliers = os.path.join( outputDirectory, 
                                           "dw_shell2_wo_outlier.ima" )
  fileNameShell2Outliers = os.path.join( outputDirectory, "shell2_outlier.py" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiOutlierFilter',
      'parameters' : \
        { 'fileNameT2' : str( fileNameT2 ),
          'fileNameDW' : str( fileNameDwShell2 ),
          'fileNameMask' : str( fileNameMask ),
          'sliceAxis' : 'z',
          'fileNameCorrectedDW' : str( fileNameDwShell2Outliers ),
          'fileNameOutliers' : str( fileNameShell2Outliers ),
          'outlierFactor' : 3.0,
          'radius' : 3.6,
          'thresholdRatio' : 0.04,
          'volumeFormat' : 'gis',
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameDwShell3 = os.path.join( subjectDirectoryQSpaceSamplingAddition, 
                                   "dw_shell3.ima" )
  fileNameDwShell3Outliers = os.path.join( outputDirectory, 
                                           "dw_shell3_wo_outlier.ima" )
  fileNameShell3Outliers = os.path.join( outputDirectory, "shell3_outlier.py" )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiOutlierFilter',
      'parameters' : \
        { 'fileNameT2' : str( fileNameT2 ),
          'fileNameDW' : str( fileNameDwShell3 ),
          'fileNameMask' : str( fileNameMask ),
          'sliceAxis' : 'z',
          'fileNameCorrectedDW' : str( fileNameDwShell3Outliers ),
          'fileNameOutliers' : str( fileNameShell3Outliers ),
          'outlierFactor' : 3.0,
          'radius' : 3.6,
          'thresholdRatio' : 0.04,
          'volumeFormat' : 'gis',
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  # copyFile( fileNameDw, fileNameDwOutliers )
  # copyFile( fileNameDw[ : -3 ] + 'dim', fileNameDwOutliers[ : -3 ] + 'dim' )
  # copyFile( fileNameDw + '.minf', fileNameDwOutliers + '.minf' )

  fileNameDwOutliers = os.path.join( outputDirectory, 'dw_wo_outlier.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Cat',
      'parameters' : \
        { 'inputNames' : ( str( fileNameDwShell1Outliers ), 
                           str( fileNameDwShell2Outliers ),
                           str( fileNameDwShell3Outliers ) ),
          'outputName' : str( fileNameDwOutliers ),
          'type' : 't',
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameDw = os.path.join( subjectDirectoryQSpaceSamplingAddition, "dw.ima" )

  copyFile( fileNameDw + '.minf', fileNameDwOutliers + '.minf' )

  fileNameT2Outliers = os.path.join( outputDirectory, "t2_wo_outlier.ima" )

  copyFile( fileNameT2, fileNameT2Outliers )
  copyFile( fileNameT2[ : -3 ] + 'dim', fileNameT2Outliers[ : -3 ] + 'dim' )

  fileNameRGBOutliers = os.path.join( outputDirectory, 
                                      'dti_rgb_wo_outliers.ima' )

  gkg.executeCommand( { 'algorithm' : 'DwiTensorField',
                        'parameters' : \
                          { 'fileNameT2' : str( fileNameT2Outliers ),
                            'fileNameDW' : str( fileNameDwOutliers ),
                            'fileNameMask' : str( fileNameMask ),
                            'tensorFunctorNames' : ( 'rgb' ),
                            'outputFileNames' : str( fileNameRGBOutliers ),
                            'outputOrientationCount' : 0,
                            'radius' : -1.0,
                            'thresholdRatio' : 0.01,
                            'volumeFormat' : 'gis',
                            'meshMapFormat' : 'aimsmesh',
                            'textureMapFormat' : 'aimstexture',
                            'rgbScale' : 1.0,
                            'meshScale' : 1.0,
                            'lowerFAThreshold' : 0.0,
                            'upperFAThreshold' : 1.0,
                            'specificScalarParameters' : (),
                            'specificStringParameters' : \
                                                 ( 'robust_positive_definite' ),
                            'ascii' : False,
                            'verbose' : verbose
                          },
                        'verbose' : verbose
                      } )


  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
