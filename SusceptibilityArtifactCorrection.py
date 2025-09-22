import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def getSize( fileNameIma ):

  f = open( fileNameIma[ : -3 ] + 'dim', 'r' )
  lines = f.readlines()
  f.close()
  line1 = lines[ 0 ].split()
  sizeX = int( line1[ 0 ] )
  sizeY = int( line1[ 1 ] )
  sizeZ = int( line1[ 2 ] )
  sizeT = int( line1[ 3 ] )

  return [ sizeX, sizeY, sizeZ, sizeT ]

def runSusceptibilityArtifactCorrection( subjectDirectoryOutlierCorrection,
                                         subjectDirectoryGisConversion,
                                         subjectDirectoryMaskFromMorphologist,
                                         subjectsParametersDictionary,
                                         outputDirectory,
                                         verbose ):
                      
  
  if ( verbose == True ):
  
    print( "SUSCEPTIBILITY ARTIFACT CORRECTION" )
    print( "-------------------------------------------------------------" )
  
  fileNameT2 = os.path.join( subjectDirectoryOutlierCorrection, 
                             't2_wo_outlier.ima' )
  fileNameDw = os.path.join( subjectDirectoryOutlierCorrection, 
                             'dw_wo_outlier.ima' )
  fileNameB0Magnitude = os.path.join( subjectDirectoryGisConversion, 
                                      '09-b0-magnitude.ima' )
  fileNameB0Phase = os.path.join( subjectDirectoryGisConversion, 
                                  '10-b0-phase.ima' )

  fileNameFirstEchoB0Magnitude = os.path.join( outputDirectory, 
                                               'b0_magnitude_echo1.ima' )
  fileNameSecondEchoB0Magnitude = os.path.join( outputDirectory, 
                                                'b0_magnitude_echo2.ima' )
  fileNameFirstEchoB0MagnitudeMask = os.path.join( \
                                                 outputDirectory, 
                                                 'b0_magnitude_echo1_mask.ima' )

  partialFourierFactor = float( subjectsParametersDictionary[ \
                                                      "partialFourierFactor" ] )
  echoSpacing = float( subjectsParametersDictionary[ "echoSpacing" ] )
  epiFactor = int( subjectsParametersDictionary[ "EPIFactor" ] )
  deltaTE = float( subjectsParametersDictionary[ "deltaTE" ] )

  phaseNegativeSign = 1
  staticB0Field = 3.0
  echoTrainLength = epiFactor + 1
  epiPhaseSize = 64
  parallelAccelerationFactor = 2

  if ( verbose == True ):

    print( 'TE2 - TE1 : ', deltaTE, ' ms' )
    print( 'partial Fourier factor : ', partialFourierFactor )
    print( 'echo spacing : ', echoSpacing, ' ms' )
    print( 'phase sign : ', phaseNegativeSign )

  command = 'GkgExecuteCommand SubVolume' + \
            ' -i ' + fileNameB0Magnitude + \
            ' -o ' + fileNameFirstEchoB0Magnitude + \
            ' -tIndices 0' + \
            ' -verbose true'
  os.system( command )

  command = 'GkgExecuteCommand SubVolume' + \
            ' -i ' + fileNameB0Magnitude + \
            ' -o ' + fileNameSecondEchoB0Magnitude + \
            ' -tIndices 1' + \
            ' -verbose true'
  os.system( command )

  fileNameWrappedB0PhaseDifference = os.path.join( outputDirectory,
                                                   'b0_phase_wrapped.ima' )

  gkg.executeCommand(
    { 'algorithm' : 'SiemensPhaseMapConverter',
      'parameters' : \
        { 'fileNameIn' : fileNameB0Phase,
          'fileNameOut' : fileNameWrappedB0PhaseDifference,
          'outputFormat' : 'gis',
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameUnwrappedB0PhaseDifference = os.path.join( outputDirectory,
                                                     'b0_phase_unwrapped.ima' )
  fileNameB0QualityMap = os.path.join( outputDirectory, 'b0_quality_map.ima' )

  gkg.executeCommand(
    { 'algorithm' : 'PhaseUnwrapper',
      'parameters' : \
        { 'fileNameIn' : fileNameWrappedB0PhaseDifference,
          'fileNameOut' : fileNameUnwrappedB0PhaseDifference,
          'fileNameMask' : '',
          'fileNameQuality' : fileNameB0QualityMap,
          'offset' : 0.0,
          'scale' : 1.0,
          'planeAxis' : 'z',
          'cycleCount' : 2,
          'coarsestSize' : 3,
          'preSmoothingIterationCount' : 2,
          'postSmoothingIterationCount' : 2,
          'useCongruence' : True,
          'qualityThreshold' : 0.9,
          'removeRampFlag' : True,
          'ascii' : False,
          'format' : 'gis',
          'applyMaskToOutput' : False,
          'removeBias' : False,
          'fileNameBias' : '',
          'maximumFitOrder' : 8,
          'maximumBiasOrder' : 2,
          'zUnwrappingType' : 1,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameB0ToDwTransform3d = os.path.join( outputDirectory, 'b0_to_dw.trm' )
  fileNameDwToB0Transform3d = os.path.join( outputDirectory, 'dw_to_b0.trm' )

  gkg.executeCommand(
    { 'algorithm' : 'Registration3d',
      'parameters' : \
        { 'referenceName' : fileNameFirstEchoB0Magnitude,
          'floatingName' : fileNameT2,
          'outputName' : fileNameDwToB0Transform3d,
          'outputInverseName' : fileNameB0ToDwTransform3d,
          'similarityMeasureName' : 'mutual-information',
          'optimizerName' : 'nelder-mead',
          'referenceLowerThreshold' : 0.0,
          'floatingLowerThreshold' : 0.0,
          'resamplingOrder' : 1,
          'subSamplingMaximumSizes' : 64,
          'similarityMeasureParameters' : ( 32, 1 ),
          'optimizerParameters' : ( 1000, 0.01,
                                    10, 10, 10,
                                    10, 10, 10 ),
          'transformType' : 'rigid',
          'initialParameters' : ( 0, 0, 0,
                                  0, 0, 0 ),
          'initialTrmName' : '',
          'intermediateFileName' : '',
          'ignoreHeaderTransformations' : True,
          'initializedUsingCentreOfGravity' : True,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  # resampling unwrapped phase difference map
  fileNameResampledUnwrappedB0PhaseDifference = os.path.join( \
                                            outputDirectory,
                                            'b0_phase_unwrapped_resampled.ima' )

  sizes = getSize( fileNameUnwrappedB0PhaseDifference )

  gkg.executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : fileNameUnwrappedB0PhaseDifference,
          'outSize' : ( sizes[ 0 ], sizes[ 1 ], sizes[ 2 ] ),
          'outResolution' : ( 4, 4, 4 ),
          'fileNameTransforms' : fileNameB0ToDwTransform3d,
          'fileNameOut' : fileNameResampledUnwrappedB0PhaseDifference,
          'order' : 3,
          'outBackground' : 0.0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  # computing phase to pixel factor
  phaseToPixelFactor = ( float( epiPhaseSize ) * partialFourierFactor / \
                         float( parallelAccelerationFactor ) ) * \
                        ( echoSpacing / ( 2 * 3.14159265359 * deltaTE ) ) * \
                        phaseNegativeSign

  if ( verbose == True ):

    print( 'phase to pixel factor : ', phaseToPixelFactor )

  # correcting geometrical distortions of T2 due to susceptibility effects
  fileNameT2WoSusceptibility = os.path.join(  outputDirectory,
                                              't2_wo_susceptibility.ima' )
  fileNameSusceptibilityShiftMap = os.path.join( \
                                                outputDirectory,
                                                'susceptibility_shift_map.ima' )

  gkg.executeCommand(
    { 'algorithm' : 'B0InhomogeneityCorrection',
      'parameters' : \
        { 'fileNameDistortedVolume' : fileNameT2,
          'fileNamePhaseDifferenceVolume' : \
                                    fileNameResampledUnwrappedB0PhaseDifference,
          'fileNameUndistortedVolume' : fileNameT2WoSusceptibility,
          'fileNameShiftVolume' : fileNameSusceptibilityShiftMap,
          'phaseAxis' : 'y',
          'phaseToPixelFactorInformation' : phaseToPixelFactor,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
                                          
  # correcting geometrical distortions of DW due to susceptibility effects
  fileNameDWWoSusceptibility = os.path.join( outputDirectory,
                                             'dw_wo_susceptibility.ima' )

  gkg.executeCommand(
    { 'algorithm' : 'B0InhomogeneityCorrection',
      'parameters' : \
        { 'fileNameDistortedVolume' : fileNameDw,
          'fileNamePhaseDifferenceVolume' : \
                                    fileNameResampledUnwrappedB0PhaseDifference,
          'fileNameUndistortedVolume' : fileNameDWWoSusceptibility,
          'phaseAxis' : 'y',
          'phaseToPixelFactorInformation' : phaseToPixelFactor,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameRGBWoSusceptibility = os.path.join( outputDirectory, 
                                              'dti_rgb_wo_susceptibility.ima' )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist, 
                               'mask.ima' )

  gkg.executeCommand( { 'algorithm' : 'DwiTensorField',
                        'parameters' : \
                          { 'fileNameT2' : fileNameT2WoSusceptibility,
                            'fileNameDW' : fileNameDWWoSusceptibility,
                            'fileNameMask' : fileNameMask,
                            'tensorFunctorNames' : ( 'rgb' ),
                            'outputFileNames' : fileNameRGBWoSusceptibility,
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
