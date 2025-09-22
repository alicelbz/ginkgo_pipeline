import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runTractographySRP( subjectLocalModelingQBIDirectory,
                        subjectDirectoryMaskFromMorphologist,
                        outputDirectory,
                        verbose ):
                      
  
  if ( verbose == True ):
  
    print( "STREAMLINE REGULARIZED PROBABILISTIC TRACTOGRAPHY" )
    print( "-------------------------------------------------------------" )

  fileNameAQbiOdfSiteMap = os.path.join( subjectLocalModelingQBIDirectory,
                                         'aqbi_odf_site_map' )
  fileNameAQbiOdfTextureMap = os.path.join( subjectLocalModelingQBIDirectory,
                                            'aqbi_odf_texture_map' )
  fileNameHighResolutionMask = os.path.join( \
                                           subjectDirectoryMaskFromMorphologist,
                                           'mask_high_resolution.ima' )

  fileNameBundles = os.path.join( outputDirectory, 'tractography.bundles' )
                                  
  gkg.executeCommand(
    { 'algorithm' : 'DwiTractography',
      'parameters' : \
        { 'fileNameSiteMap' : fileNameAQbiOdfSiteMap,
          'fileNameOdfs' : fileNameAQbiOdfTextureMap,
          'fileNameRois' : fileNameHighResolutionMask,
          'fileNameMask' : fileNameHighResolutionMask,
          'fileNameRoisToOdfsTransform3d' : '',
          'fileNameMaskToOdfsTransform3d' : '',
          'fileNameBundleMap' : fileNameBundles,
          'algorithmType' : 'streamline-probabilistic',
          'algorithmScalarParameters' : ( 8, 0.5, 5, 1.0,
                                          300.0, 30.0, 1.0, 0.0, 0.12, 0, 0 ),
          'algorithmStringParameters' : (),
          'outputOrientationCount' : 500,
          'bundleMapFormat' : 'aimsbundlemap',
          'volumeFormat' : 'gis',
          'stepCount' : 8,
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )
    
  for i in range( 1, 9 ):

    fileNameClusters = os.path.join( 
                                    outputDirectory,
                                    'tractography_' + str( i ) + '_8.clusters' )

    fileNameSplitBundles = os.path.join( 
                                     outputDirectory,
                                     'tractography_' + str( i ) + '_8.bundles' )

    copyFile( fileNameSplitBundles, fileNameClusters )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
