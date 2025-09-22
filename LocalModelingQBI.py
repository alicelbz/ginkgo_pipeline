import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runLocalModelingQBI( fileNameDw,
                         subjectDirectoryEddyCurrentAndMotionCorrection,
                         subjectDirectoryMaskFromMorphologist,
                         outputDirectory,
                         verbose ):
                      
  
  if ( verbose == True ):
  
    print( "LOCAL MODELING USING QBI MODEL" )
    print( "-------------------------------------------------------------" )

  fileNameT2 = os.path.join( subjectDirectoryEddyCurrentAndMotionCorrection,
                             't2_wo_eddy_current.ima' )
  fileNameMask = os.path.join( subjectDirectoryMaskFromMorphologist,
                               'mask.ima' )

  fileNameAQbiGFA = os.path.join( outputDirectory, 'aqbi_gfa' )
  fileNameAQbiRGB = os.path.join( outputDirectory, 'aqbi_rgb' )
  fileNameAQbiOdfSiteMap = os.path.join( outputDirectory, 'aqbi_odf_site_map' )
  fileNameAQbiOdfTextureMap = os.path.join( outputDirectory,
                                            'aqbi_odf_texture_map' )

  gkg.executeCommand(
    { 'algorithm' : 'DwiOdfField',
      'parameters' : \
        { 'fileNameT2' : str( fileNameT2 ),
          'fileNameDW' : str( fileNameDw ),
          'fileNameMask' : fileNameMask,
          'modelType' : 'aqball_odf_cartesian_field',
          'odfFunctorNames' : ( 'gfa',
                                'rgb',
                                'odf_site_map',
                                'odf_texture_map' ),
          'outputFileNames' : ( fileNameAQbiGFA,
                                fileNameAQbiRGB,
                                fileNameAQbiOdfSiteMap,
                                fileNameAQbiOdfTextureMap ),
          'outputOrientationCount' : 0,
          'radius' : -1.0,
          'thresholdRatio' : 0.01,
          'volumeFormat' : 'gis',
          'meshMapFormat' : 'aimsmesh',
          'textureMapFormat' : 'aimstexture',
          'rgbScale' : 1.0,
          'meshScale' : 1.0,
          'lowerFAThreshold' : 0.0,
          'upperFAThreshold' : 1.0,
          'specificScalarParameters' : ( 8, 0.006, 0.0 ),
          'specificStringParameters' : (),
          'furtherScalarParameters' : (),
          'furtherStringParameters' : (),
          'ascii' : False,
          'verbose' : verbose
        },
      'verbose' : verbose
    } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
