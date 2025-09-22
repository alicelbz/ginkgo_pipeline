import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runConnectivityMatrix( subjectDirectoryTractographySRD,
                           subjectDirectoryMaskFromMorphologist,
                           subjectDirectoryFreeSurferParcellation,
                           subjectDirectoryNormalization,
                           outputDirectory,
                           verbose ):
                      
  
  if ( verbose == True ):
  
    print( "CONNECTIVITY MATRIX FROM TRACTOGRAPHY FROM " +
           os.path.basename( subjectDirectoryTractographySRD ) )
    print( "-------------------------------------------------------------" )

  fileNameAtlasLabelsNii = os.path.join( subjectDirectoryFreeSurferParcellation,
                                         '04-GiftiAndNifti',
                                         'aparc.a2009s+aseg.nii.gz' )

  fileNameAtlasLabels = os.path.join( outputDirectory, 
                                      'aparc.a2009s+aseg.ima' )

  command = "AimsReplaceLevel" + \
            " -i " + fileNameAtlasLabelsNii + \
            " -o " + fileNameAtlasLabels + \
            " -g 2 4 5 7 14 15 16 24 30 31 41 43 44 46 62 63 77 85 251 252 253 254 255 " + \
            " -n 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 " + \
            " --verbose "
  print( command )
  os.system( command )
  
  command = "AimsFileConvert" + \
            " -i " + fileNameAtlasLabels + \
            " -o " + fileNameAtlasLabels + \
            " -t S16 " + \
            " --verbose "
  print( command )
  os.system( command )
  removeMinf( fileNameAtlasLabels )

  fileNameT1ToDwTransform3d = os.path.join( subjectDirectoryMaskFromMorphologist, 
                                            't1-to-dw.trm' )
  fileNameConnectivityMatrix = os.path.join( outputDirectory,
                                             'connectivity-matrix.mat' )
  fileNameAverageLengthMatrix = os.path.join( outputDirectory,
                                              'average-length-matrix.mat' )
  fileNameRoiToRoiBundleMap = os.path.join( outputDirectory,
                                            'roi-to-roi-bundle-map.bundles' )

  fileNameTractogramSRD = os.path.join( subjectDirectoryTractographySRD, 
                                        'tractography.bundles' )

  CommandFactory().executeCommand(
    { 'algorithm' : 'DwiConnectivityMatrix',
      'parameters' : \
        { 'fileNameBundleMaps' : str( fileNameTractogramSRD ),
          'fileNameVolumeROIs1' : str( fileNameAtlasLabels ),
          'fileNameROIs1ToBundleMapTransform3d' : str( fileNameT1ToDwTransform3d ),
          'scalarParameters' : ( 1, 0.1, 1.0, 0, 0, 1, 100, 100, 100 ),
          'functorNames' : ( 'connectivity-matrix', 
                             'average-length-matrix', 
                             'roi-to-roi-bundle-map' ),
          'outputFileNames' : ( str( fileNameConnectivityMatrix ), 
                                str( fileNameAverageLengthMatrix ),
                                str( fileNameRoiToRoiBundleMap ) ),
          'outputBundleMapFormat' : 'aimsbundlemap',
          'outputTextureMapFormat' : 'aimstexture',
          'doNotCheckLabelTypes' : False,
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
    
  fileNameBundlesForRendering = os.path.join( outputDirectory, 
                                              'tractography_10percent.bundles' )

  fileNameAtlasHippocampiLabels = os.path.join( outputDirectory, 
                                                'hippocampi.ima' )


  command = 'AimsSelectLabel ' + \
            ' -i ' + fileNameAtlasLabels + \
            ' -o ' + fileNameAtlasHippocampiLabels + \
            ' -l 17 53 ' + \
            ' -b 0 --verbose'
  os.system( command )

  fileNameRoiToRoiHippocampiBundleMap = os.path.join( outputDirectory, 
                                                      'roi-to-roi-hippocampi.bundles' )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameRoiToRoiBundleMap ),
            'fileNameOutputBundleMaps' : str( fileNameRoiToRoiHippocampiBundleMap ),
            'operatorName' : 'roi-based-selection',
            'stringParameters' : ( fileNameAtlasHippocampiLabels, fileNameT1ToDwTransform3d, 'ge', 'intersection' ),
            'scalarParameters' : ( 17, 0.0, 0.1, 0.1 ),
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  fileNameRoiToRoiHippocampiBundleMapInTemplate = os.path.join( outputDirectory, 
                                                      'roi-to-roi-hippocampi-in-template.bundles' )

  fileNameDwToTemplate = os.path.join( subjectDirectoryNormalization, 
                                       'dw-to-atlas.trm' )
  fileNameT1ToTemplate = os.path.join( subjectDirectoryNormalization, 
                                       't1-to-atlas.ima' )
  fileNameTemplateToT1 = os.path.join( subjectDirectoryNormalization, 
                                       'atlas-to-t1.ima' )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameRoiToRoiHippocampiBundleMap ),
            'fileNameOutputBundleMaps' : str( fileNameRoiToRoiHippocampiBundleMapInTemplate ),
            'operatorName' : 'transform3d',
            'stringParameters' : ( fileNameDwToTemplate, fileNameT1ToTemplate, fileNameTemplateToT1 ),
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  fileNameRoiToRoiBundleMapInTemplate = os.path.join( outputDirectory, 
                                                      'roi-to-roi-bundle-map-in-template.bundles' )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameRoiToRoiBundleMap ),
            'fileNameOutputBundleMaps' : str( fileNameRoiToRoiBundleMapInTemplate ),
            'operatorName' : 'transform3d',
            'stringParameters' : ( fileNameDwToTemplate, fileNameT1ToTemplate, fileNameTemplateToT1 ),
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )

