import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runDicomConversion( subjectRawDataDirectory,
                        description,
                        outputDirectory,
                        verbose ):
                      
  
  if ( verbose == True ):
  
    print( "DICOM CONVERSION" )
    print( "-------------------------------------------------------------" )
  
  for key in sorted( description.keys() ):
    
    directoryNameIn = os.path.join( subjectRawDataDirectory,
                                    description[ key ] )
                                    
    directoryNameOut = os.path.join( outputDirectory, key )


    if ( verbose == True ):
    
      print( directoryNameIn + " -> " + directoryNameOut )

    copyDirectory( directoryNameIn, directoryNameOut )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
