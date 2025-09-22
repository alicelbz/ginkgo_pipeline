import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runShortFiberLabelling( subjectDirectoryTractography,
                            subjectDirectoryMaskFromMorphologist,
                            outputDirectory,
                            verbose ):
                      
  
  if ( verbose == True ):
  
    print( "SHORT FIBER LABELLING" )
    print( "-------------------------------------------------------------" )

  fileNameBundles = os.path.join( subjectDirectoryTractography, 
                                  'tractography.bundles' )

  fileNameTransform3dBundleMapToAtlas = os.path.join( \
                                           subjectDirectoryMaskFromMorphologist, 
                                           'dw-to-talairach.trm' )

  gkg.executeCommand(
    { 'algorithm' : 'DwiFiberLabelling',
      'parameters' : \
        { 'fileNameInputBundleMaps' : str( fileNameBundles ),
          'targetAtlasName' : 'human-superficial-WM-bundle-atlas',
          'fileNameTransform3dBundleMapToAtlas' : \
                                            fileNameTransform3dBundleMapToAtlas,
          'fiberResamplingPointCount' : 21,
          'densityMaskFiberResamplingStep' : 0.1,
          'densityMaskResolution' : ( 1.0, 1.0, 1.0 ),
          'outputDirectoryName' : outputDirectory,
          'intermediate' : False,
          'singleFile' : True,
          'computeDensityMasks' : True,
          'saveDiscarded' : False,
          'outputVolumeFormat' : 'gis',
          'outputBundleFormat' : 'aimsbundlemap',
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  fileNameWMBundles = os.path.join( outputDirectory, 
                                    'white_matter_bundles.bundles' )

  # ordering extremities
  fileNameOrderedWMBundles = os.path.join( 
                                        outputDirectory,
                                        'white_matter_bundles-ordered.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameWMBundles ),
            'fileNameOutputBundleMaps' : str( fileNameOrderedWMBundles ),
            'operatorName' : 'order-extremities',
            'scalarParameters' : 100,
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  # calculating centroids
  fileNameWMCentroids = os.path.join( outputDirectory,
                                      'white_matter_centroids.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( fileNameOrderedWMBundles ),
            'fileNameOutputBundleMaps' : str( fileNameWMCentroids ),
            'operatorName' : 'compute-centroids',
            'stringParameters' : 
                            ( "average-fiber", 
                              "all", 
                              "symmetric-mean-of-mean-closest-point-distance" ),
            'scalarParameters' : ( 10000, 100, 0 ),
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
