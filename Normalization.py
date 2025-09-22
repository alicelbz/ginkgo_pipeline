import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runNormalization( subjectDirectoryMaskFromMorphologist,
                      templateDirectory,
                      outputDirectory,
                      verbose ):
                      
  
  if ( verbose == True ):
  
    print( "NORMALIZATION" )
    print( "-------------------------------------------------------------" )


  fileNameT1 = os.path.join( subjectDirectoryMaskFromMorphologist, 'nobias_t1.ima' )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist, 'mask_t1.ima' )

  # masking T2
  fileNameT1Masked = os.path.join( outputDirectory, 't1-masked.ima' )
  gkg.executeCommand(
    { 'algorithm' : 'Combiner',
      'parameters' : \
        { 'fileNameIns' : fileNameT1,
          'fileNameOut' : fileNameT1Masked,
          'functor1s' : 'id',
          'functor2s' : 'id',
          'numerator1s' : ( 1.0, 1.0 ),
          'denominator1s' : ( 1.0, 1.0 ),
          'numerator2s' : 1.0,
          'denominator2s' : 1.0,
          'operators' : '*',
          'fileNameMask' : fileNameMask,
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
  removeMinf( fileNameT1Masked )

  # performing ANTs linear+diffeomorphic registration

  fileNameAtlasT1 = os.path.join( templateDirectory, 
                                  'mni_icbm152_t1_tal_nlin_asym_09a_masked.ima' )
  
  fileNameAtlasInT1Space = os.path.join( outputDirectory, 
                                         'atlas-in-t1-space.ima' )
  fileNameT1InAtlasSpace = os.path.join( outputDirectory, 
                                         't1-in-atlas-space.ima' )

  fileNameDirectTransform = os.path.join( outputDirectory,
                                          't1-to-atlas' )
  fileNameInverseTransform = os.path.join( outputDirectory,
                                           'atlas-to-t1' )
  command = 'GkgAntsRegistration3d' + \
            ' -r ' + fileNameAtlasT1 + \
            ' -f ' + fileNameT1Masked + \
            ' -d ' + fileNameDirectTransform + \
            ' -i ' + fileNameInverseTransform + \
            ' -t affine_and_diffeomorphic' + \
            ' -R ' + fileNameAtlasInT1Space + \
            ' -F ' + fileNameT1InAtlasSpace + \
            ' -I True' + \
            ' --verbose'
  os.system( command )
  removeMinf( fileNameAtlasInT1Space )
  removeMinf( fileNameT1InAtlasSpace )

  fileNameDwtoT1Transform = os.path.join( subjectDirectoryMaskFromMorphologist,
                                          'dw-to-t1.trm' )

  fileNameDwtoAtlasTransform = os.path.join( outputDirectory,
                                          'dw-to-atlas.trm' )

  command = 'GkgExecuteCommand Transform3dComposer' + \
            ' -i ' + fileNameDwtoT1Transform + ' ' + fileNameDirectTransform + '.trm' + \
            ' -o ' + fileNameDwtoAtlasTransform + \
            ' -verbose'
  os.system( command )

  fileNameAtlasToDwTransform = os.path.join( outputDirectory,
                                             'atlas-to-dw.trm' )

  command = 'GkgExecuteCommand Transform3dInverter' + \
            ' -i ' + fileNameDwtoAtlasTransform + \
            ' -o ' + fileNameAtlasToDwTransform + \
            ' -verbose'
  os.system( command )
  
  # to put in FiberFiltering.py

#  fileNameInputBundles = 
#  fileNameBundlesInTemplateSpace = 

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( fileNameInputBundles ),
#            'fileNameOutputBundleMaps' : str( fileNameBundlesInTemplateSpace ),
#            'operatorName' : 'transform3d',
#            'stringParameters' : ( fileNameDwtoAtlasTransform, 
#                                   fileNameDirectTransform + '.ima', 
#                                   fileNameInverseTransform + '.ima' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )


  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
