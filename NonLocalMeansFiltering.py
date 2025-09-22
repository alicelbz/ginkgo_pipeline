import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runNonLocalMeansFiltering( subjectOrientationAndBValueFileDecodingDirectory,
                               outputDirectory,
                               verbose ):
                      
  
  if ( verbose == True ):
  
    print( "NON-LOCAL MEANS FILTERING" )
    print( "-------------------------------------------------------------" )
  

  fileNameT2 = os.path.join( subjectOrientationAndBValueFileDecodingDirectory,
                             "t2.ima" )
  fileNameDw = os.path.join( subjectOrientationAndBValueFileDecodingDirectory,
                             "dw.ima" )
  fileNameT2NLM = os.path.join( outputDirectory, 't2-filtered.ima' )
  fileNameDwNLM = os.path.join( outputDirectory, 'dw-filtered.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'NonLocalMeansFilter',
      'parameters' :
        { 'fileNameIn' : fileNameT2,
          'fileNameOut' : fileNameT2NLM,
          'noiseModel' : 'nonCentralChi',
          'halfSearchBlocSize' : 8,
          'halfNeighborhoodSize' : 1,
          'degreeOfFiltering' : 0.3,
          'sigma' : 12,
          'n' : 32,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
  removeMinf( fileNameT2NLM )

  CommandFactory().executeCommand(
    { 'algorithm' : 'NonLocalMeansFilter',
      'parameters' :
        { 'fileNameIn' : fileNameDw,
          'fileNameOut' : fileNameDwNLM,
          'noiseModel' : 'nonCentralChi',
          'halfSearchBlocSize' : 8,
          'halfNeighborhoodSize' : 1,
          'degreeOfFiltering' : 0.3,
          'sigma' : 12,
          'n' : 32,
          'ascii' : False,
          'format' : 'gis',
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
  removeMinf( fileNameDwNLM )

#  copyFile( fileNameT2, fileNameT2NLM )
#  copyFile( fileNameT2[ : -3 ] + 'dim', fileNameT2NLM[ : -3 ] + 'dim' )
#
#  copyFile( fileNameDw, fileNameDwNLM )
#  copyFile( fileNameDw[ : -3 ] + 'dim', fileNameDwNLM[ : -3 ] + 'dim' )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
