import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runGisConversion( subjectRawDataDirectory,
                      description,
                      differentMatrixSequences,
                      timePoint,
                      outputDirectory,
                      verbose ):


  if ( verbose == True ):

    print( "GIS CONVERSION" )
    print( "-------------------------------------------------------------" )

  for key in sorted( description.keys() ):

    directoryNameIn = os.path.join( subjectRawDataDirectory,
                                    description[ key ] )

    fileNameOut = os.path.join( outputDirectory, key + '.ima' )

    gkg.executeCommand(
      { 'algorithm' : 'Dicom2GisConverter',
        'parameters' : \
          { 'fileNameIn' : str( directoryNameIn ),
            'fileNameOut' : str( fileNameOut ),
            'outputFormat' : 'gis',
            'noFlip' : False,
            'noDemosaic' : False,
            'verbose' : verbose
            },
        'verbose' : verbose
        } )
    removeMinf( fileNameOut )

    gkg.executeCommand(
      { 'algorithm' : 'Combiner',
        'parameters' : \
          { 'fileNameIns' : str( fileNameOut ),
            'fileNameOut' : str( fileNameOut ),
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
            'outputType' : 'float',
            'ascii' : False,
            'format' : 'gis',
            'verbose' : verbose
            },
        'verbose' : verbose
        } )
    removeMinf( fileNameOut )

    if timePoint in differentMatrixSequences:

      if key in differentMatrixSequences[ timePoint ]:

        fileNameIdentityMatrix = os.path.join( outputDirectory, 'id.trm' )

        with open( fileNameIdentityMatrix, 'w') as f:
          f.write('0 0 0\n')
          f.write('1 0 0\n')
          f.write('0 1 0\n')
          f.write('0 0 1\n')
          f.close()

        gkg.executeCommand(
          { 'algorithm' : 'Resampling3d',
            'parameters' : \
              { 'fileNameReference' : str( fileNameOut ),
                'outSize' : (128, 128, 70),
                'outResolution' : (2, 2, 2),
                'fileNameTransforms': str( fileNameIdentityMatrix ),
                'fileNameOut' : str( fileNameOut ),
                'order' : 3,
                'outBackground' : 0.0,
                'ascii' : False,
                'format' : 'gis',
                'verbose' : verbose
                },
            'verbose' : verbose
            } )
      removeMinf( fileNameOut )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
