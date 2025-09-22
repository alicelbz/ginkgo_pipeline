import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runFiberLengthHistogramSRD( subjectTractographySRDDirectory,
                                outputDirectory,
                                verbose ):
                      
  
  if ( verbose == True ):
  
    print( "HISTOGRAM OF FIBER LENGTHS FROM TRACTOGRAM SRD" )
    print( "-------------------------------------------------------------" )

  fileNameTractogramSRD = os.path.join( subjectTractographySRDDirectory, 
                                            'tractography.bundles' )

  fiberLengthHistogram = os.path.join( outputDirectory, 
                                       'fiber_length_histogram' )
                                    
  fiberLengthHistogramPython = os.path.join( outputDirectory, 
                                             'fiber_length_histogram' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( fileNameTractogramSRD ),
            'fileNameMeasure' : fiberLengthHistogram,
            'measureNames' : 'bundle_fiber_length_histogram',
            'scalarParameters' : ( 1, 100 ),
            'stringParameters' : fiberLengthHistogramPython,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
