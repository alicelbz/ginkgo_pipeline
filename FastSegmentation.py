import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *


from CopyFileDirectoryRm import *

def runFASTSegmentation( subjectDirectoryMorphologist,
                         outputDirectory,
                         verbose ):
                      
  
  if ( verbose == True ):
  
    print( "FAST grey/white/CSF segmentation" )
    print( "-------------------------------------------------------------" )
                                        
  fileNameT1 = os.path.join( subjectDirectoryMorphologist, 'nobias_t1.ima' )
  # fileNameT1Mask = os.path.join( subjectDirectoryMorphologist, 'mask_t1.ima' )
  fileNameT1Mask = os.path.join( subjectDirectoryMorphologist, 'left_and_right_hemispheres_mask.ima' )

  fileNameT1Masked = os.path.join( outputDirectory, 't1-mprage-masked.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Combiner',
      'parameters' : \
        { 'fileNameIns' : str( fileNameT1 ),
          'fileNameOut' : str( fileNameT1Masked ),
          'functor1s' : 'id',
          'functor2s' : 'id',
          'numerator1s' : ( 1.0, 1.0 ),
          'denominator1s' : ( 1.0, 1.0 ),
          'numerator2s' : 1.0,
          'denominator2s' : 1.0,
          'operators' : '*',
          'fileNameMask' : str( fileNameT1Mask ),
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

  fileNameT1MaskedNifti = os.path.join( outputDirectory, 
                                        't1-mprage-masked.nii' )

  CommandFactory().executeCommand(
      { 'algorithm' : 'Gis2NiftiConverter',
        'parameters' : \
        { 'fileNameIn' : str( fileNameT1Masked ),
          'fileNameOut' : str( fileNameT1MaskedNifti ),
          'verbose' : verbose
        },
        'verbose' : verbose
      } )

  fileNameOutput = os.path.join( outputDirectory, 'fast' )
  command = 'fast -n 2 -o ' + fileNameOutput + ' -v ' + fileNameT1MaskedNifti
  print( command )
  os.system( command )

  fileNameFASTOutNifti = os.path.join( outputDirectory, 'fast_pveseg.nii.gz' )
  fileNameFASTOut = os.path.join( outputDirectory, 'fast_pveseg.ima' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'Nifti2GisConverter',
      'parameters' : \
      { 'fileNameIn' : str( fileNameFASTOutNifti ),
        'fileNameOut' : str( fileNameFASTOut ),
        'outputFormat' : 'gis',
        'ascii' : False,
        'verbose' : verbose
      },
      'verbose' : verbose
    } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
