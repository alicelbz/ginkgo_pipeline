import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runFiberLengthHistogramSRP( subjectTractographySRPDirectory,
                                outputDirectory,
                                verbose ):
                      
  
  if ( verbose == True ):
  
    print( "HISTOGRAM OF FIBER LENGTHS FROM TRACTOGRAM SRP" )
    print( "-------------------------------------------------------------" )

  fileNameTractogramSRP = os.path.join( subjectTractographySRPDirectory,  
                                        'tractography_' )

  fileNameFullTractogramSRP = os.path.join( outputDirectory, 
                                            'tractography.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : ( \
                                 str( fileNameTractogramSRP ) + '1_8.bundles',
                                 str( fileNameTractogramSRP ) + '2_8.bundles',
                                 str( fileNameTractogramSRP ) + '3_8.bundles',
                                 str( fileNameTractogramSRP ) + '4_8.bundles',
                                 str( fileNameTractogramSRP ) + '5_8.bundles',
                                 str( fileNameTractogramSRP ) + '6_8.bundles',
                                 str( fileNameTractogramSRP ) + '7_8.bundles',
                                 str( fileNameTractogramSRP ) + '8_8.bundles' ),
            'fileNameOutputBundleMaps' : fileNameFullTractogramSRP,
            'operatorName' : 'fusion',
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  fiberLengthHistogram = os.path.join( outputDirectory, 
                                       'fiber_length_histogram' )
                                    
  fiberLengthHistogramPython = os.path.join( outputDirectory, 
                                             'fiber_length_histogram' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( fileNameFullTractogramSRP ),
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
