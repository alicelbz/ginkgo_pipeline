import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runFlipping( subjectGisDataDirectory,
                 flippingTypes,
                 description,
                 outputDirectory,
                 verbose ):
                      
  
  if ( verbose == True ):
  
    print( "FLIPPING" )
    print( "-------------------------------------------------------------" )
  
  for key in sorted( description.keys() ):
    
    fileNameIn = os.path.join( subjectGisDataDirectory, key + '.ima' )
    fileNameOut = os.path.join( outputDirectory, key + '.ima' )

    gkg.executeCommand(
    { 'algorithm' : 'Flipper',
      'parameters' : \
        { 'fileNameIn' : str( fileNameIn ),
          'fileNameOut' : str( fileNameOut ),
          'stringTypes' : flippingTypes,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
    removeMinf( fileNameOut )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
