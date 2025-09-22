import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runRoughMaskExtraction( subjectDirectoryQSpaceSamplingAddition,
                            outputDirectory,
                            verbose ):
                      
  
  if ( verbose == True ):
  
    print( "ROUGH MASK EXTRACTON FROM DW DATA" )
    print( "-------------------------------------------------------------" )
                        
  fileNameT2 = os.path.join( subjectDirectoryQSpaceSamplingAddition, "t2.ima" )
  fileNameMaskStep1 = os.path.join( outputDirectory, 'mask_step1.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'GetMask',
      'parameters' : \
      { 'fileNameIn' : str( fileNameT2 ),
        'fileNameOut' : str( fileNameMaskStep1 ),
        'algorithmType' : 2,
        'outType' : 'int16_t',
        'radius' : 1.0,
        'noisePosition' : 0.9,
        'noiseRatio' : 0.01,
        'thrown' : 20,
        'kept' : 100,
        'thresholdRatio' : 0.009,
        'foreground' : 1,
        'background' : 0,
        'ascii' : False,
        'format' : 'gis',
        'verbose' : verbose
      },
      'verbose' : verbose
    } )

  fileNameMaskStep2 = os.path.join( outputDirectory, "mask_step2.ima" )

  CommandFactory().executeCommand(
  { 'algorithm' : 'MorphologicalOperation',
    'parameters' : \
      { 'fileNameIn' : str( fileNameMaskStep1 ),
        'fileNameOut' : str( fileNameMaskStep2 ),
        'operation' : 'erosion',
        'radius' : 9.0,
        'neighborhood' : 18,
        'outType' : 'int16_t',
        'mode' : 'gt',
        'threshold1' : 0,
        'foreground' : 1,
        'background' : 0,
        'ascii' : False,
        'format' : 'gis',
        'verbose' : True
      },
    'verbose' : verbose
  } )

  fileNameMaskStep3 = os.path.join( outputDirectory, "mask_step3.ima" )

  command = 'GkgExecuteCommand ConnectedComponents ' + \
            ' -i ' + fileNameMaskStep2 + \
            ' -o ' + fileNameMaskStep3 + \
            ' -c 1 -r 0 -m gt -t1 0 -verbose ' 
  os.system( command )

  fileNameMaskStep4 = os.path.join( outputDirectory, "mask_step4.ima" )

  CommandFactory().executeCommand(
  { 'algorithm' : 'MorphologicalOperation',
    'parameters' : \
      { 'fileNameIn' : str( fileNameMaskStep3 ),
        'fileNameOut' : str( fileNameMaskStep4 ),
        'operation' : 'dilation',
        'radius' : 9.0,
        'neighborhood' : 18,
        'outType' : 'int16_t',
        'mode' : 'gt',
        'threshold1' : 0,
        'foreground' : 1,
        'background' : 0,
        'ascii' : False,
        'format' : 'gis',
        'verbose' : True
      },
    'verbose' : verbose
  } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
