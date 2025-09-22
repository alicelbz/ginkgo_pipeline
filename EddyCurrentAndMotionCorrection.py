import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runEddyCurrentAndMotionCorrection( subjectDirectoryOutlierCorrection,
                                       subjectDirectoryMaskFromMorphologist,
                                       outputDirectory,
                                       verbose ):
                      
  
  if ( verbose == True ):
  
    print( "EDDY CURRENT AND MOTION CORRECTION" )
    print( "-------------------------------------------------------------" )

  fileNameT2 = os.path.join( subjectDirectoryOutlierCorrection,
                             "t2_wo_outlier.ima" )
  fileNameDw = os.path.join( subjectDirectoryOutlierCorrection,
                             "dw_wo_outlier.ima" )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist, 
                               "mask.ima" )

  fileNameDwWoEddyCurrentStep1 = os.path.join( outputDirectory,
                                               'dw_wo_eddy_current_step1.ima' )
  fileNameEddyCurrentProfilesStep1 = os.path.join( \
                                             outputDirectory,
                                             'eddy_current_profiles_step1.txt' )

  gkg.executeCommand( { 'algorithm' : 'DwiEddyCurrent',
                        'parameters' : \
                          { 'inputName' : fileNameDw,
                            'referenceRank' : 0,
                            'referenceName' : fileNameT2,
                            'outputName' : fileNameDwWoEddyCurrentStep1,
                            'similarityMeasureName' : 'mutual-information',
                            'optimizerName' : 'nelder-mead',
                            'lowerThreshold' : 0.0,
                            'registrationResamplingOrder' : 1,
                            'subSamplingMaximumSizes' : ( 64 ),
                            'similarityMeasureParameters' : ( 64.0, 1.0 ),
                            'optimizerParameters' : ( 1000, 0.01,
                                                      0.05, 0.05, 0.05,
                                                      0.02, 0.02, 0.02,
                                                      10.0, 10.0, 10.0,
                                                      2.0, 2.0, 2.0 ),
                            'initialParameters' : ( 1.0, 1.0, 1.0,
                                                    0.0, 0.0, 0.0,
                                                    0.0, 0.0, 0.0,
                                                    0.0, 0.0, 0.0 ),
                            'outputResamplingOrder' : 3,
                            'background' : 0.0,
                            'furtherSliceCountAlongX' : 0,
                            'furtherSliceCountAlongY' : 0,
                            'furtherSliceCountAlongZ' : 0,
                            'correctQSpaceSampling' : True,
                            'eddyCurrentProfileName' : \
                                               fileNameEddyCurrentProfilesStep1,
                            'verboseRegistration' : False,
                            'verbose' : verbose
                          },
                        'verbose' : verbose
                      } )

  fileNameDwGeometricMean = os.path.join( outputDirectory,
                                          'dw_geometric_mean.ima' )

  gkg.executeCommand( { 'algorithm' : 'DwiGeometricMean',
                        'parameters' : \
                          { 'fileNameInput' : fileNameDwWoEddyCurrentStep1,
                            'fileNameOutput' : fileNameDwGeometricMean
                          },
                        'verbose' : verbose
                      } )

  fileNameDwWoEddyCurrentStep2 = os.path.join( outputDirectory,
                                               'dw_wo_eddy_current_step2.ima' )
  fileNameEddyCurrentProfilesStep2 = os.path.join( 
                                             outputDirectory,
                                             'eddy_current_profiles_step2.txt' )
  gkg.executeCommand( { 'algorithm' : 'DwiEddyCurrent',
                        'parameters' : \
                          { 'inputName' : fileNameDw,
                            'referenceRank' : 0,
                            'referenceName' : fileNameDwGeometricMean,
                            'outputName' : fileNameDwWoEddyCurrentStep2,
                            'similarityMeasureName' : 'mutual-information',
                            'optimizerName' : 'nelder-mead',
                            'lowerThreshold' : 0.0,
                            'registrationResamplingOrder' : 1,
                            'subSamplingMaximumSizes' : ( 64 ),
                            'similarityMeasureParameters' : ( 64.0, 1.0 ),
                            'optimizerParameters' : ( 1000, 0.01,
                                                      0.05, 0.05, 0.05,
                                                      0.02, 0.02, 0.02,
                                                      10.0, 10.0, 10.0,
                                                      2.0, 2.0, 2.0 ),
                            'initialParameters' : ( 1.0, 1.0, 1.0,
                                                    0.0, 0.0, 0.0,
                                                    0.0, 0.0, 0.0,
                                                    0.0, 0.0, 0.0 ),
                            'outputResamplingOrder' : 3,
                            'background' : 0.0,
                            'furtherSliceCountAlongX' : 0,
                            'furtherSliceCountAlongY' : 0,
                            'furtherSliceCountAlongZ' : 0,
                            'correctQSpaceSampling' : True,
                            'eddyCurrentProfileName' : \
                                              fileNameEddyCurrentProfilesStep2,
                            'verboseRegistration' : False,
                            'verbose' : verbose
                          },
                        'verbose' : verbose
                      } )

  fileNameDwWoEddyCurrent = os.path.join( outputDirectory,
                                          'dw_wo_eddy_current.ima' )

  gkg.executeCommand( { 'algorithm' : 'Thresholder',
                        'parameters' : \
                          { 'fileNameIn' : fileNameDwWoEddyCurrentStep2,
                            'fileNameOut' : fileNameDwWoEddyCurrent,
                            'mode' : 'ge',
                            'threshold1' : 0.0,
                            'threshold2' : 0.0,
                            'background' : 0.0,
                            'ascii' : False,
                            'format' : 'gis',
                            'verbose' : verbose
                          },
                        'verbose' : verbose
                      } )

  fileNameT2WoEddyCurrent = os.path.join( outputDirectory,
                                          't2_wo_eddy_current.ima' )

  copyFile( fileNameT2, fileNameT2WoEddyCurrent )
  copyFile( fileNameT2[ : -3 ] + 'dim', 
            fileNameT2WoEddyCurrent[ : -3 ] + 'dim' )
  copyFile( fileNameT2 + '.minf', fileNameT2WoEddyCurrent + '.minf' )

  fileNameRGBWoEddyCurrent = os.path.join( outputDirectory, 
                                           'dti_rgb_wo_eddy_current.ima' )

  gkg.executeCommand( { 'algorithm' : 'DwiTensorField',
                        'parameters' : \
                          { 'fileNameT2' : fileNameT2WoEddyCurrent,
                            'fileNameDW' : fileNameDwWoEddyCurrent,
                            'fileNameMask' : fileNameMask,
                            'tensorFunctorNames' : ( 'rgb' ),
                            'outputFileNames' : fileNameRGBWoEddyCurrent,
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

  fileNameSplittedShells = os.path.join( outputDirectory, "dw" )

  gkg.executeCommand( { 'algorithm' : 'DwiMultipleShellQSpaceSamplingSplitter',
                        'parameters' : \
                          { 'fileNameInputDW' : str( fileNameDwWoEddyCurrent ),
                            'fileNameOutputDW' : str( fileNameSplittedShells ),
                            'verbose' : verbose
                          },
                        'verbose' : verbose
                      } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
