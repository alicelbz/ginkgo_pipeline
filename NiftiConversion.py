import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runNiftiConversion( subjectGisDataDirectory,
                        description,
                        outputDirectory,
                        verbose ):
                      
  
  if ( verbose == True ):
  
    print( "NIFTI CONVERSION" )
    print( "-------------------------------------------------------------" )
  
  for key in sorted( description.keys() ):
    
    fileNameIn = os.path.join( subjectGisDataDirectory, key + '.ima' )
    fileNameOut = os.path.join( outputDirectory, key + '.nii.gz' )

    CommandFactory().executeCommand(
        { 'algorithm' : 'Gis2NiftiConverter',
          'parameters' : \
          { 'fileNameIn' : str( fileNameIn ),
            'fileNameOut' : str( fileNameOut ),
            'verbose' : verbose
          },
          'verbose' : verbose
        } )

    if ( key.startswith( 'dw' ) ):
    
      fileNameOutB0 = os.path.join( outputDirectory, 'b0' + key[2:] + '.ima' )

      command = 'GkgExecuteCommand SubVolume ' + \
                '-i ' + fileNameIn + ' ' + \
                '-o ' + fileNameOutB0 + ' ' + \
                '-T 0 ' + \
                '-verbose'
      print( command )
      os.system( command )
      removeMinf( fileNameOutB0 )
      
      fileNameOutB0Nifti = os.path.join( outputDirectory, 
                                         'b0' + key[2:] + '.nii.gz' )

      CommandFactory().executeCommand(
          { 'algorithm' : 'Gis2NiftiConverter',
            'parameters' : \
            { 'fileNameIn' : str( fileNameOutB0 ),
              'fileNameOut' : str( fileNameOutB0Nifti ),
              'verbose' : verbose
            },
            'verbose' : verbose
          } )
    
    
  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
