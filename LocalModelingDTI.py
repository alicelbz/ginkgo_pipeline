import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runLocalModelingDTI( fileNameDw,
                         subjectDirectoryEddyCurrentAndMotionCorrection,
                         subjectDirectoryMaskFromMorphologist,
                         outputDirectory,
                         verbose ):
                      
  
  if ( verbose == True ):
  
    print( "LOCAL MODELING USING DTI MODEL" )
    print( "-------------------------------------------------------------" )

  fileNameT2 = os.path.join( subjectDirectoryEddyCurrentAndMotionCorrection,
                             't2_wo_eddy_current.ima' )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist,
                               'mask.ima' )

  fileNameFA = os.path.join( outputDirectory, 'dti_fa' )
  fileNameRGB = os.path.join( outputDirectory, 'dti_rgb' )
  fileNameADC = os.path.join( outputDirectory, 'dti_adc' )
  fileNameParallelDiffusivity = os.path.join( outputDirectory,
                                              'dti_parallel_diffusivity' )
  fileNameTransverseDiffusivity = os.path.join( outputDirectory,
                                                'dti_transverse_diffusivity' )

  gkg.executeCommand( { 'algorithm' : 'DwiTensorField',
                        'parameters' : \
                          { 'fileNameT2' : str( fileNameT2 ),
                            'fileNameDW' : str( fileNameDw ),
                            'fileNameMask' : fileNameMask,
                            'tensorFunctorNames' : ( 'fa',
                                                     'rgb',
                                                     'adc',
                                                     'lambda_parallel',
                                                     'lambda_transverse' ),
                            'outputFileNames' : \
                                              ( fileNameFA,
                                                fileNameRGB,
                                                fileNameADC,
                                                fileNameParallelDiffusivity,
                                                fileNameTransverseDiffusivity ),
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

  fileNameADCWoMask = os.path.join( outputDirectory, 'dti_adc_wo_mask' )

  gkg.executeCommand( { 'algorithm' : 'DwiTensorField',
                        'parameters' : \
                          { 'fileNameT2' : fileNameT2,
                            'fileNameDW' : fileNameDw,
                            'fileNameMask' : '',
                            'tensorFunctorNames' : 'adc',
                            'outputFileNames' : fileNameADCWoMask,
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
