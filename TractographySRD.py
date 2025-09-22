import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runTractographySRD( subjectLocalModelingQBIDirectory,
                        subjectDirectoryMaskFromMorphologist,
                        outputDirectory,
                        verbose ):
                      
  
  if ( verbose == True ):
  
    print( "STREAMLINE REGULARIZED DETERMINISTIC TRACTOGRAPHY" )
    print( "-------------------------------------------------------------" )

  fileNameAQbiOdfSiteMap = os.path.join( subjectLocalModelingQBIDirectory,
                                         'aqbi_odf_site_map' )
  fileNameAQbiOdfTextureMap = os.path.join( subjectLocalModelingQBIDirectory,
                                            'aqbi_odf_texture_map' )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist,
                               'mask.ima' )

  fileNameBundles = os.path.join( outputDirectory, 'tractography.bundles' )

  gkg.executeCommand(
    { 'algorithm' : 'DwiTractography',
      'parameters' : \
        { 'fileNameSiteMap' : str( fileNameAQbiOdfSiteMap ),
          'fileNameOdfs' : str( fileNameAQbiOdfTextureMap ),
          'fileNameRois' : str( fileNameMask ),
          'fileNameMask' : str( fileNameMask ),
          'fileNameRoisToOdfsTransform3d' : '',
          'fileNameMaskToOdfsTransform3d' : '',
          'fileNameBundleMap' : str( fileNameBundles ),
          'algorithmType' : 'streamline-regularized-deterministic',
          'algorithmScalarParameters' : ( 0.5, 6, 1, 300.0, 30.0, -1, -1 ),
          'algorithmStringParameters' : (),
          'seedingStrategyType' : 'unconstrained',
          'seedingRegionIds' : 1,
          'seedingSamplingTypes' : 'cartesian',
          'seedingSeedPerVoxelCounts' : 8,
          'stoppingStrategyType' : 'mask-and-gfa',
          'stoppingStrategyScalarParameters' : ( 0, 0 ),
          'outputOrientationCount' : 500,
          'bundleMapFormat' : 'aimsbundlemap',
          'volumeFormat' : 'gis',
          'stepCount' : 1,
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameBundlesForRendering = os.path.join( outputDirectory, 
                                              'tractography_10percent.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameBundles ),
            'fileNameOutputBundleMaps' : str( fileNameBundlesForRendering ),
            'operatorName' : 'random-selection',
            'scalarParameters' : 10,
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
