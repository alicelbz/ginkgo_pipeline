import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

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

def runMaskFromMorphologistPipeline( subjectDirectoryGisConversion,
                                     subjectDirectoryQSpaceSamplingAddition,
                                     fileNameT1APC,
                                     outputDirectory,
                                     verbose ):
                      
  
  if ( verbose == True ):
  
    print( "COMPUTING MASK FROM MORPHOLOGIST PIPELINE" )
    print( "-------------------------------------------------------------" )

  fileNameUnbiasedT1 = os.path.join( outputDirectory, 'nobias_t1.ima' )
  fileNameBiasFieldT1 = os.path.join( outputDirectory, 'biasfield_t1' )
  fileNameWhiteRidgeT1 = os.path.join( outputDirectory, 'whiteridge_t1' )
  fileNameEdgesT1 = os.path.join( outputDirectory, 'edges_t1' )
  fileNameVarianceT1 = os.path.join( outputDirectory, 'variance_t1' )
  fileNameMeanCurvatureT1 = os.path.join( outputDirectory, 'mean_curvature_t1' )
  fileNameHFilteredT1 = os.path.join( outputDirectory, 'hfiltered_t1' )

  fileNameT1 = os.path.join( subjectDirectoryGisConversion, 't1-mprage.ima' )
  fileNameT2 = os.path.join( subjectDirectoryQSpaceSamplingAddition, 't2.ima' )

  fileNameT1S16 = os.path.join( outputDirectory, 't1-S16.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Combiner',
      'parameters' : \
        { 'fileNameIns' : str( fileNameT1 ),
          'fileNameOut' : str( fileNameT1S16 ),
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

  command = 'VipT1BiasCorrection' +  \
            ' -i ' + fileNameT1S16 + \
            ' -o ' + fileNameUnbiasedT1 + \
            ' -Fwrite no ' + \
            ' -field ' + fileNameBiasFieldT1 + '.ima' + \
            ' -Wwrite yes ' + \
            ' -wridge ' + fileNameWhiteRidgeT1 + '.ima' + \
            ' -Kregul 20.0' + \
            ' -sampling 16.0' + \
            ' -Kcrest 20.0' + \
            ' -Grid 2' + \
            ' -ZregulTuning 0.5' + \
            ' -vp 75' + \
            ' -e 3' + \
            ' -eWrite yes' + \
            ' -ename ' + fileNameEdgesT1 + '.ima' +  \
            ' -vWrite yes' + \
            ' -vname ' + fileNameVarianceT1 + '.ima' + \
            ' -mWrite no' +  \
            ' -mname ' + fileNameMeanCurvatureT1 + '.ima' + \
            ' -hWrite yes' + \
            ' -hname ' + fileNameHFilteredT1 + '.ima' +  \
            ' -Last \'auto (AC/PC Points needed)\'' + \
            ' -Points ' + fileNameT1APC
  os.system( command )

  fileNameHistogramAnalysis = os.path.join( outputDirectory, 't1.han' )

  command = 'VipHistoAnalysis' + \
            ' -i ' + fileNameUnbiasedT1 + \
            ' -o ' + fileNameHistogramAnalysis + \
            ' -Save y ' + \
            ' -Mask ' + fileNameHFilteredT1 + '.ima' + \
            ' -Ridge ' + fileNameWhiteRidgeT1 + '.ima' +  \
            ' -mode i'
  os.system( command )

  fileNameBrainT1 = os.path.join( outputDirectory, 'mask_t1.ima' )

  command = 'VipGetBrain' + \
            ' -i ' + fileNameUnbiasedT1 + \
            ' -berosion 1.8' + \
            ' -analyse r ' + \
            ' -hname ' + fileNameHistogramAnalysis + \
            ' -bname ' + fileNameBrainT1 + \
            ' -First 0 ' + \
            ' -Last 0 ' + \
            ' -layer 0 ' + \
            ' -Points ' + fileNameT1APC + \
            ' -m V ' + \
            ' -Variancename ' + fileNameVarianceT1 + '.ima' +  \
            ' -Edgesname ' + fileNameEdgesT1 + '.ima' +  \
            ' -Ridge ' + fileNameWhiteRidgeT1 + '.ima'
  os.system( command )
  removeMinf( fileNameBrainT1 )

  fileNameBrainVolumeTxt = os.path.join( outputDirectory, 'mask_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + fileNameBrainT1 + \
            ' > ' + fileNameBrainVolumeTxt
  os.system( command )  

  fileNameVoronoiMask = os.path.join( outputDirectory, 'voronoi_t1.ima' )
  fileNameClosedVoronoi = os.path.join( os.sep, 
                                        'usr', 
                                        'share', 
                                        'gkg', 
                                        'data',
                                        'Human', 
                                        'templates', 
                                        'closedvoronoi.ima' )

  command = 'VipSplitBrain' + \
            ' -input ' + fileNameUnbiasedT1 + \
            ' -brain ' + fileNameBrainT1 + \
            ' -analyse r ' + \
            ' -hname ' + fileNameHistogramAnalysis + \
            ' -output ' + fileNameVoronoiMask + \
            ' -mode \'Watershed (2011)\'' + \
            ' -erosion 2.0 ' + \
            ' -ccsize 500 ' + \
            ' -Points ' + fileNameT1APC + \
            ' -walgo b ' + \
            ' -Bary 0.6 ' + \
            ' -template ' + fileNameClosedVoronoi + \
            ' -TemplateUse y ' + \
            ' -Ridge ' + fileNameWhiteRidgeT1 + '.ima'
  os.system( command )
  removeMinf( fileNameVoronoiMask )

  fileNameLeftAndRightHemisphereMask = os.path.join(
                                             outputDirectory,
                                             'left_and_right_hemispheres_mask' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Binarizer',
      'parameters' : \
        { 'fileNameIn' : str( fileNameVoronoiMask ),
          'fileNameOut' : str( fileNameLeftAndRightHemisphereMask ),
          'outType' : 'int16_t',
          'mode' : 'be',
          'threshold1' : 1,
          'threshold2' : 2,
          'foreground' : 32767,
          'background' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  
  removeMinf( fileNameLeftAndRightHemisphereMask )

  fileNameTalairachTransform = os.path.join(
                          outputDirectory,
                          'RawT1-t1_default_acquisition_TO_Talairach-ACPC.trm' )

  command = 'VipTalairachTransform' + \
            ' -i ' + fileNameT1APC + \
            ' -o ' + fileNameTalairachTransform + \
            ' -m ' + fileNameLeftAndRightHemisphereMask
  os.system( command )  

  fileNameDwToT1Transform3d = os.path.join( outputDirectory, 'dw-to-t1.trm' )
  fileNameT1ToDwTransform3d = os.path.join( outputDirectory, 't1-to-dw.trm' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Registration3d',
      'parameters' : \
        { 'referenceName' : str( fileNameUnbiasedT1 ),
          'floatingName' : str( fileNameT2 ),
          'outputName' : fileNameDwToT1Transform3d,
          'outputInverseName' : fileNameT1ToDwTransform3d,
          'similarityMeasureName' : 'mutual-information',
          'optimizerName' : 'nelder-mead',
          'referenceLowerThreshold' : 0.0,
          'floatingLowerThreshold' : 0.0,
          'resamplingOrder' : 1,
          'subSamplingMaximumSizes' : 64,
          'similarityMeasureParameters' : ( 32, 1 ),
          'optimizerParameters' : ( 1000, 0.01,
                                    2, 2, 2,
                                    5, 10, 10 ),
          'transformType' : 'rigid',
          'initialParameters' : ( 0.0, 0.0, 0.0,
                                  0.0, 0.0, 0.0 ),
          'initialTrmName' : '',
          'intermediateFileName' : '',
          'ignoreHeaderTransformations' : True,
          'initializedUsingCentreOfGravity' : True,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameDwToTalairachTransform = os.path.join( outputDirectory,
                                                 'dw-to-talairach.trm' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Transform3dComposer',
      'parameters' : \
        { 'fileNameIns' : ( fileNameDwToT1Transform3d, 
                            fileNameTalairachTransform ),
          'fileNameOut' : str( fileNameDwToTalairachTransform ),
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  fileNameMask = os.path.join( outputDirectory, 'mask.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Resampling3d',
      'parameters' : \
        { 'fileNameReference' : str( fileNameBrainT1 ),
          'fileNameTemplate' : str( fileNameT2 ),
          'fileNameTransforms' : fileNameT1ToDwTransform3d,
          'fileNameOut' : fileNameMask,
          'order' : 0,
          'outBackground' : 0,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )  

  command = 'AimsReplaceLevel' + \
            ' -i ' + fileNameMask + \
            ' -o ' + fileNameMask + \
            ' -g 255 -n 1 --verbose '
  os.system( command )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
