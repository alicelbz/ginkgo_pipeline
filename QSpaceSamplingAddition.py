import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runQSpaceSamplingAddition( subjectOrientationAndBValueFileDecodingDirectory,
                               outputDirectory,
                               verbose ):
                      
  
  if ( verbose == True ):
  
    print( "Q-SPACE SAMPLING ADDITION" )
    print( "-------------------------------------------------------------" )
  

  fileNameT2NLM = os.path.join( subjectOrientationAndBValueFileDecodingDirectory,
                                't2.ima' )        
  fileNameDwNLM = os.path.join( subjectOrientationAndBValueFileDecodingDirectory,
                                'dw.ima' )        
  fileNameBValues = os.path.join(
                               subjectOrientationAndBValueFileDecodingDirectory,
                               'bvalues.txt' )
  fileNameOrientations = os.path.join(
                               subjectOrientationAndBValueFileDecodingDirectory,
                               'bvec.txt' )
  fileNameT2 = os.path.join( outputDirectory, 't2.ima' )
  fileNameDw = os.path.join( outputDirectory, 'dw.ima' )

  copyFile( fileNameT2NLM, fileNameT2 )
  copyFile( fileNameT2NLM[ : -3 ] + 'dim', fileNameT2[ : -3 ] + 'dim' )

  copyFile( fileNameDwNLM, fileNameDw )
  copyFile( fileNameDwNLM[ : -3 ] + 'dim', fileNameDw[ : -3 ] + 'dim' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiQSpaceSampling',
      'parameters' : \
        { 'fileNameDW' : fileNameDw,
          'stringParameters' : ( 'spherical', 
                                 'multiple-shell',
                                 'different-orientation-sets',
                                 'custom',
                                 fileNameBValues,
                                 fileNameOrientations ),
          'scalarParameters' : 200, 
          'coefficients' : ( 1.0, 0.0, 0.0, 0.0,
                             0.0, 1.0, 0.0, 0.0,
                             0.0, 0.0, 1.0, 0.0,
                             0.0, 0.0, 0.0, 1.0 ),
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameDwSplittedShells = os.path.join( outputDirectory, 'dw' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiMultipleShellQSpaceSamplingSplitter',
      'parameters' : \
        { 'fileNameInputDW' : fileNameDw,
          'fileNameOutputDW' : str( fileNameDwSplittedShells ),
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
  

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
