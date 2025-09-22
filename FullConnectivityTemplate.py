import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *

def runFullConnectivityTemplate( subjectV1ConnectivityMatrixDirectories,
                                 subjectV2ConnectivityMatrixDirectories,
                                 subjectV3ConnectivityMatrixDirectories,
                                 outputDirectory,
                                 verbose ):
                      
  
  if ( verbose == True ):
  
    print( "FULL CONNECTIVITY TEMPLATE" )
    print( "-------------------------------------------------------------" )

#  #############################################################################
#  # V1
#  #############################################################################

#  fileNameV1Bundles = ()

#  for i in range( len( subjectV1ConnectivityMatrixDirectories ) ):

#    if os.path.exists( os.path.join( \
#                                subjectV1ConnectivityMatrixDirectories[i],
#                                'roi-to-roi-bundle-map-in-template.bundles' ) ):

#      fileNameV1Bundles += ( str( os.path.join( \
#                              subjectV1ConnectivityMatrixDirectories[i],
#                              'roi-to-roi-bundle-map-in-template.bundles' ) ), )

#  # fusion V1
  fileNameFullV1ConnectivityTemplate = os.path.join( 
                                       outputDirectory,
                                       'full-v1-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : fileNameV1Bundles,
#            'fileNameOutputBundleMaps' : str( 
#                                           fileNameFullV1ConnectivityTemplate ),
#            'operatorName' : 'fusion',
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # ordering extremities
#  fileNameFullV1ConnectivityOrderedTemplate = os.path.join( 
#                               outputDirectory,
#                               'full-v1-connectivity-ordered-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV1ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                    fileNameFullV1ConnectivityOrderedTemplate ),
#            'operatorName' : 'order-extremities',
#            'scalarParameters' : 100,
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # calculating centroids
#  fileNameFullV1ConnectivityCentroidsTemplate = os.path.join( 
#                                outputDirectory,
#                                'full-v1-connectivity-centroids-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                    fileNameFullV1ConnectivityOrderedTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                  fileNameFullV1ConnectivityCentroidsTemplate ),
#            'operatorName' : 'compute-centroids',
#            'stringParameters' : 
#                            ( "average-fiber", 
#                              "all", 
#                              "symmetric-mean-of-mean-closest-point-distance" ),
#            'scalarParameters' : ( 10000, 100, 0 ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  # extracting hippocampi clusters 17 and 53
  fileNameHippocampiV1ConnectivityTemplate = os.path.join( 
                                 outputDirectory,
                                 'hippocampi-v1-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV1ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV1ConnectivityTemplate ),
#            'operatorName' : 'select-labels',
#            'stringParameters' : ( '53_11101', '53_11102', '53_11103', '53_11105', '53_11106', '53_11107', '53_11108', '53_11109', '53_11110', '53_11111', '53_11112', '53_11113', '53_11114', '53_11115', '53_11116', '53_11117', '53_11118', '53_11119', '53_11120', '53_11121', '53_11122', '53_11123', '53_11124', '53_11125', '53_11126', '53_11127', '53_11128', '53_11129', '53_11130', '53_11131', '53_11132', '53_11133', '53_11134', '53_11135', '53_11136', '53_11137', '53_11138', '53_11139', '53_11141', '53_11143', '53_11144', '53_11145', '53_11146', '53_11147', '53_11149', '53_11151', '53_11152', '53_11153', '53_11154', '53_11155', '53_11157', '53_11158', '53_11159', '53_11161', '53_11162', '53_11164', '53_11165', '53_11166', '53_11167', '53_11168', '53_11169', '53_11170', '53_11171', '53_11172', '53_11173', '53_11174', '53_12101', '53_12102', '53_12103', '53_12104', '53_12105', '53_12106', '53_12107', '53_12108', '53_12109', '53_12110', '53_12111', '53_12112', '53_12113', '53_12114', '53_12115', '53_12116', '53_12117', '53_12118', '53_12119', '53_12120', '53_12121', '53_12122', '53_12123', '53_12124', '53_12125', '53_12126', '53_12127', '53_12128', '53_12129', '53_12130', '53_12131', '53_12132', '53_12133', '53_12134', '53_12135', '53_12136', '53_12137', '53_12138', '53_12139', '53_12140', '53_12141', '53_12143', '53_12144', '53_12145', '53_12146', '53_12147', '53_12148', '53_12149', '53_12150', '53_12151', '53_12152', '53_12153', '53_12154', '53_12155', '53_12156', '53_12157', '53_12158', '53_12159', '53_12160', '53_12161', '53_12162', '53_12163', '53_12164', '53_12165', '53_12166', '53_12167', '53_12168', '53_12169', '53_12170', '53_12171', '53_12172', '53_12173', '53_12174', '53_12175', '53_54', '53_58', '53_60', '53_80', '17_11101', '17_11102', '17_11103', '17_11104', '17_11105', '17_11106', '17_11107', '17_11108', '17_11109', '17_11110', '17_11111', '17_11112', '17_11113', '17_11114', '17_11115', '17_11116', '17_11117', '17_11118', '17_11119', '17_11120', '17_11121', '17_11122', '17_11123', '17_11124', '17_11125', '17_11126', '17_11127', '17_11128', '17_11129', '17_11130', '17_11131', '17_11132', '17_11133', '17_11134', '17_11135', '17_11136', '17_11137', '17_11138', '17_11139', '17_11140', '17_11141', '17_11143', '17_11144', '17_11145', '17_11146', '17_11147', '17_11148', '17_11149', '17_11150', '17_11151', '17_11152', '17_11153', '17_11154', '17_11155', '17_11156', '17_11157', '17_11158', '17_11159', '17_11160', '17_11161', '17_11162', '17_11163', '17_11164', '17_11165', '17_11166', '17_11167', '17_11168', '17_11169', '17_11170', '17_11171', '17_11172', '17_11173', '17_11174', '17_11175', '17_12101', '17_12102', '17_12103', '17_12105', '17_12108', '17_12109', '17_12110', '17_12111', '17_12113', '17_12114', '17_12115', '17_12116', '17_12117', '17_12118', '17_12119', '17_12120', '17_12121', '17_12122', '17_12123', '17_12124', '17_12125', '17_12127', '17_12128', '17_12129', '17_12130', '17_12131', '17_12132', '17_12133', '17_12134', '17_12135', '17_12136', '17_12137', '17_12138', '17_12139', '17_12141', '17_12143', '17_12144', '17_12145', '17_12146', '17_12147', '17_12148', '17_12149', '17_12150', '17_12151', '17_12152', '17_12153', '17_12155', '17_12157', '17_12158', '17_12159', '17_12161', '17_12162', '17_12163', '17_12164', '17_12165', '17_12166', '17_12167', '17_12168', '17_12172', '17_12173', '17_12174', '17_12175', '17_18', '17_26', '17_28', '17_47', '17_49', '17_50', '17_51', '17_52', '17_53', '17_54', '17_58', '17_60', '17_80' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameHippocampiV1ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV1ConnectivityTemplate ),
#            'operatorName' : 'discard-labels',
#            'stringParameters' : ( '11117_11118', '11117_11119', '11117_11120', '11117_11121', '11117_11122', '11117_11123', '11117_11124', '11117_11125', '11117_11126', '11117_11127', '11117_11128', '11117_11129', '11117_11130', '11117_11131', '11117_11132', '11117_11133', '11117_11134', '11117_11135', '11117_11136', '11117_11137', '11117_11138', '11117_11139', '11117_11140', '11117_11141', '11117_11143', '11117_11144', '11117_11145', '11117_11146', '11117_11147', '11117_11148', '11117_11149', '11117_11150', '11117_11151', '11117_11152', '11117_11153', '11117_11154', '11117_11155', '11117_11156', '11117_11157', '11117_11158', '11117_11159', '11117_11160', '11117_11161', '11117_11162', '11117_11163', '11117_11164', '11117_11165', '11117_11166', '11117_11167', '11117_11168', '11117_11169', '11117_11170', '11117_11171', '11117_11172', '11117_11173', '11117_11174', '11117_11175', '11117_12101', '11117_12103', '11117_12105', '11117_12108', '11117_12110', '11117_12111', '11117_12113', '11117_12114', '11117_12115', '11117_12116', '11117_12117', '11117_12118', '11117_12119', '11117_12120', '11117_12121', '11117_12122', '11117_12123', '11117_12124', '11117_12125', '11117_12127', '11117_12129', '11117_12130', '11117_12131', '11117_12132', '11117_12134', '11117_12135', '11117_12138', '11117_12139', '11117_12143', '11117_12144', '11117_12145', '11117_12146', '11117_12147', '11117_12148', '11117_12150', '11117_12151', '11117_12153', '11117_12155', '11117_12157', '11117_12159', '11117_12162', '11117_12163', '11117_12164', '11117_12165', '11117_12166', '11117_12167', '11117_12172', '11117_12174', '11117_12175', '11153_11154', '11153_11155', '11153_11157', '11153_11158', '11153_11159', '11153_11161', '11153_11162', '11153_11164', '11153_11165', '11153_11166', '11153_11167', '11153_11168', '11153_11169', '11153_11170', '11153_11171', '11153_11172', '11153_11173', '11153_11174', '11153_12101', '11153_12103', '11153_12104', '11153_12105', '11153_12106', '11153_12107', '11153_12108', '11153_12109', '11153_12110', '11153_12112', '11153_12113', '11153_12114', '11153_12115', '11153_12116', '11153_12117', '11153_12118', '11153_12124', '11153_12125', '11153_12126', '11153_12129', '11153_12130', '11153_12132', '11153_12138', '11153_12139', '11153_12140', '11153_12146', '11153_12147', '11153_12148', '11153_12150', '11153_12153', '11153_12154', '11153_12155', '11153_12163', '11153_12167', '11153_12168', '11153_12169', '11153_12170', '11153_12171', '11153_12172', '11153_12174', '12117_12118', '12117_12119', '12117_12120', '12117_12121', '12117_12122', '12117_12123', '12117_12124', '12117_12125', '12117_12127', '12117_12128', '12117_12129', '12117_12130', '12117_12131', '12117_12132', '12117_12133', '12117_12134', '12117_12135', '12117_12136', '12117_12137', '12117_12138', '12117_12139', '12117_12141', '12117_12143', '12117_12144', '12117_12145', '12117_12146', '12117_12147', '12117_12148', '12117_12149', '12117_12150', '12117_12151', '12117_12152', '12117_12153', '12117_12155', '12117_12157', '12117_12158', '12117_12159', '12117_12161', '12117_12162', '12117_12163', '12117_12164', '12117_12165', '12117_12166', '12117_12167', '12117_12168', '12117_12172', '12117_12173', '12117_12174', '12117_12175', '12153_12154', '12153_12155', '12153_12156', '12153_12157', '12153_12158', '12153_12159', '12153_12160', '12153_12161', '12153_12162', '12153_12163', '12153_12166', '12153_12167', '12153_12168', '12153_12169', '12153_12170', '12153_12171', '12153_12172', '12153_12173', '12153_12174', '12153_12175' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  # ordering extremities V1
  fileNameHippocampiV1ConnectivityOrderedTemplate = os.path.join( 
                               outputDirectory,
                               'hippocampi-v1-connectivity-ordered-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                           fileNameHippocampiV1ConnectivityTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                    fileNameHippocampiV1ConnectivityOrderedTemplate ),
            'operatorName' : 'order-extremities',
            'scalarParameters' : 100,
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  # calculating centroids V1
  fileNameHippocampiV1ConnectivityCentroidsTemplate = os.path.join( 
                             outputDirectory,
                             'hippocampi-v1-connectivity-centroids-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                    fileNameHippocampiV1ConnectivityOrderedTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                  fileNameHippocampiV1ConnectivityCentroidsTemplate ),
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

#  #############################################################################
#  # V2
#  #############################################################################

#  fileNameV2Bundles = ()

#  for i in range( len( subjectV2ConnectivityMatrixDirectories ) ):

#    if os.path.exists( os.path.join( \
#                                subjectV2ConnectivityMatrixDirectories[i],
#                                'roi-to-roi-bundle-map-in-template.bundles' ) ):

#      fileNameV2Bundles += ( str( os.path.join( \
#                              subjectV2ConnectivityMatrixDirectories[i],
#                              'roi-to-roi-bundle-map-in-template.bundles' ) ), )

##  # fusion V2
#  fileNameFullV2ConnectivityTemplate = os.path.join( 
#                                       outputDirectory,
#                                       'full-v2-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : fileNameV2Bundles,
#            'fileNameOutputBundleMaps' : str( 
#                                           fileNameFullV2ConnectivityTemplate ),
#            'operatorName' : 'fusion',
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # ordering extremities
#  fileNameFullV2ConnectivityOrderedTemplate = os.path.join( 
#                               outputDirectory,
#                               'full-v2-connectivity-ordered-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV2ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                    fileNameFullV2ConnectivityOrderedTemplate ),
#            'operatorName' : 'order-extremities',
#            'scalarParameters' : 100,
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # calculating centroids
#  fileNameFullV2ConnectivityCentroidsTemplate = os.path.join( 
#                             outputDirectory,
#                             'full-v2-connectivity-centroids-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                    fileNameFullV2ConnectivityOrderedTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                  fileNameFullV2ConnectivityCentroidsTemplate ),
#            'operatorName' : 'compute-centroids',
#            'stringParameters' : 
#                            ( "average-fiber", 
#                              "all", 
#                              "symmetric-mean-of-mean-closest-point-distance" ),
#            'scalarParameters' : ( 10000, 100, 0 ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  # extracting hippocampi clusters 17 and 53
  fileNameHippocampiV2ConnectivityTemplate = os.path.join( 
                                 outputDirectory,
                                 'hippocampi-v2-connectivity-template.bundles' )
  # ordering extremities V2
  fileNameHippocampiV2ConnectivityOrderedTemplate = os.path.join( 
                               outputDirectory,
                               'hippocampi-v2-connectivity-ordered-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                           fileNameHippocampiV2ConnectivityTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                    fileNameHippocampiV2ConnectivityOrderedTemplate ),
            'operatorName' : 'order-extremities',
            'scalarParameters' : 100,
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  # calculating centroids V2
  fileNameHippocampiV2ConnectivityCentroidsTemplate = os.path.join( 
                             outputDirectory,
                             'hippocampi-v2-connectivity-centroids-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                    fileNameHippocampiV2ConnectivityOrderedTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                  fileNameHippocampiV2ConnectivityCentroidsTemplate ),
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

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV2ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV2ConnectivityTemplate ),
#            'operatorName' : 'select-labels',
#            'stringParameters' : ( '53_11101', '53_11102', '53_11103', '53_11105', '53_11106', '53_11107', '53_11108', '53_11109', '53_11110', '53_11111', '53_11112', '53_11113', '53_11114', '53_11115', '53_11116', '53_11117', '53_11118', '53_11119', '53_11120', '53_11121', '53_11122', '53_11123', '53_11124', '53_11125', '53_11126', '53_11127', '53_11128', '53_11129', '53_11130', '53_11131', '53_11132', '53_11133', '53_11134', '53_11135', '53_11136', '53_11137', '53_11138', '53_11139', '53_11141', '53_11143', '53_11144', '53_11145', '53_11146', '53_11147', '53_11149', '53_11151', '53_11152', '53_11153', '53_11154', '53_11155', '53_11157', '53_11158', '53_11159', '53_11161', '53_11162', '53_11164', '53_11165', '53_11166', '53_11167', '53_11168', '53_11169', '53_11170', '53_11171', '53_11172', '53_11173', '53_11174', '53_12101', '53_12102', '53_12103', '53_12104', '53_12105', '53_12106', '53_12107', '53_12108', '53_12109', '53_12110', '53_12111', '53_12112', '53_12113', '53_12114', '53_12115', '53_12116', '53_12117', '53_12118', '53_12119', '53_12120', '53_12121', '53_12122', '53_12123', '53_12124', '53_12125', '53_12126', '53_12127', '53_12128', '53_12129', '53_12130', '53_12131', '53_12132', '53_12133', '53_12134', '53_12135', '53_12136', '53_12137', '53_12138', '53_12139', '53_12140', '53_12141', '53_12143', '53_12144', '53_12145', '53_12146', '53_12147', '53_12148', '53_12149', '53_12150', '53_12151', '53_12152', '53_12153', '53_12154', '53_12155', '53_12156', '53_12157', '53_12158', '53_12159', '53_12160', '53_12161', '53_12162', '53_12163', '53_12164', '53_12165', '53_12166', '53_12167', '53_12168', '53_12169', '53_12170', '53_12171', '53_12172', '53_12173', '53_12174', '53_12175', '53_54', '53_58', '53_60', '53_80', '17_11101', '17_11102', '17_11103', '17_11104', '17_11105', '17_11106', '17_11107', '17_11108', '17_11109', '17_11110', '17_11111', '17_11112', '17_11113', '17_11114', '17_11115', '17_11116', '17_11117', '17_11118', '17_11119', '17_11120', '17_11121', '17_11122', '17_11123', '17_11124', '17_11125', '17_11126', '17_11127', '17_11128', '17_11129', '17_11130', '17_11131', '17_11132', '17_11133', '17_11134', '17_11135', '17_11136', '17_11137', '17_11138', '17_11139', '17_11140', '17_11141', '17_11143', '17_11144', '17_11145', '17_11146', '17_11147', '17_11148', '17_11149', '17_11150', '17_11151', '17_11152', '17_11153', '17_11154', '17_11155', '17_11156', '17_11157', '17_11158', '17_11159', '17_11160', '17_11161', '17_11162', '17_11163', '17_11164', '17_11165', '17_11166', '17_11167', '17_11168', '17_11169', '17_11170', '17_11171', '17_11172', '17_11173', '17_11174', '17_11175', '17_12101', '17_12102', '17_12103', '17_12105', '17_12108', '17_12109', '17_12110', '17_12111', '17_12113', '17_12114', '17_12115', '17_12116', '17_12117', '17_12118', '17_12119', '17_12120', '17_12121', '17_12122', '17_12123', '17_12124', '17_12125', '17_12127', '17_12128', '17_12129', '17_12130', '17_12131', '17_12132', '17_12133', '17_12134', '17_12135', '17_12136', '17_12137', '17_12138', '17_12139', '17_12141', '17_12143', '17_12144', '17_12145', '17_12146', '17_12147', '17_12148', '17_12149', '17_12150', '17_12151', '17_12152', '17_12153', '17_12155', '17_12157', '17_12158', '17_12159', '17_12161', '17_12162', '17_12163', '17_12164', '17_12165', '17_12166', '17_12167', '17_12168', '17_12172', '17_12173', '17_12174', '17_12175', '17_18', '17_26', '17_28', '17_47', '17_49', '17_50', '17_51', '17_52', '17_53', '17_54', '17_58', '17_60', '17_80' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameHippocampiV2ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV2ConnectivityTemplate ),
#            'operatorName' : 'discard-labels',
#            'stringParameters' : ( '11117_11118', '11117_11119', '11117_11120', '11117_11121', '11117_11122', '11117_11123', '11117_11124', '11117_11125', '11117_11126', '11117_11127', '11117_11128', '11117_11129', '11117_11130', '11117_11131', '11117_11132', '11117_11133', '11117_11134', '11117_11135', '11117_11136', '11117_11137', '11117_11138', '11117_11139', '11117_11140', '11117_11141', '11117_11143', '11117_11144', '11117_11145', '11117_11146', '11117_11147', '11117_11148', '11117_11149', '11117_11150', '11117_11151', '11117_11152', '11117_11153', '11117_11154', '11117_11155', '11117_11156', '11117_11157', '11117_11158', '11117_11159', '11117_11160', '11117_11161', '11117_11162', '11117_11163', '11117_11164', '11117_11165', '11117_11166', '11117_11167', '11117_11168', '11117_11169', '11117_11170', '11117_11171', '11117_11172', '11117_11173', '11117_11174', '11117_11175', '11117_12101', '11117_12103', '11117_12105', '11117_12108', '11117_12110', '11117_12111', '11117_12113', '11117_12114', '11117_12115', '11117_12116', '11117_12117', '11117_12118', '11117_12119', '11117_12120', '11117_12121', '11117_12122', '11117_12123', '11117_12124', '11117_12125', '11117_12127', '11117_12129', '11117_12130', '11117_12131', '11117_12132', '11117_12134', '11117_12135', '11117_12138', '11117_12139', '11117_12143', '11117_12144', '11117_12145', '11117_12146', '11117_12147', '11117_12148', '11117_12150', '11117_12151', '11117_12153', '11117_12155', '11117_12157', '11117_12159', '11117_12162', '11117_12163', '11117_12164', '11117_12165', '11117_12166', '11117_12167', '11117_12172', '11117_12174', '11117_12175', '11153_11154', '11153_11155', '11153_11157', '11153_11158', '11153_11159', '11153_11161', '11153_11162', '11153_11164', '11153_11165', '11153_11166', '11153_11167', '11153_11168', '11153_11169', '11153_11170', '11153_11171', '11153_11172', '11153_11173', '11153_11174', '11153_12101', '11153_12103', '11153_12104', '11153_12105', '11153_12106', '11153_12107', '11153_12108', '11153_12109', '11153_12110', '11153_12112', '11153_12113', '11153_12114', '11153_12115', '11153_12116', '11153_12117', '11153_12118', '11153_12124', '11153_12125', '11153_12126', '11153_12129', '11153_12130', '11153_12132', '11153_12138', '11153_12139', '11153_12140', '11153_12146', '11153_12147', '11153_12148', '11153_12150', '11153_12153', '11153_12154', '11153_12155', '11153_12163', '11153_12167', '11153_12168', '11153_12169', '11153_12170', '11153_12171', '11153_12172', '11153_12174', '12117_12118', '12117_12119', '12117_12120', '12117_12121', '12117_12122', '12117_12123', '12117_12124', '12117_12125', '12117_12127', '12117_12128', '12117_12129', '12117_12130', '12117_12131', '12117_12132', '12117_12133', '12117_12134', '12117_12135', '12117_12136', '12117_12137', '12117_12138', '12117_12139', '12117_12141', '12117_12143', '12117_12144', '12117_12145', '12117_12146', '12117_12147', '12117_12148', '12117_12149', '12117_12150', '12117_12151', '12117_12152', '12117_12153', '12117_12155', '12117_12157', '12117_12158', '12117_12159', '12117_12161', '12117_12162', '12117_12163', '12117_12164', '12117_12165', '12117_12166', '12117_12167', '12117_12168', '12117_12172', '12117_12173', '12117_12174', '12117_12175', '12153_12154', '12153_12155', '12153_12156', '12153_12157', '12153_12158', '12153_12159', '12153_12160', '12153_12161', '12153_12162', '12153_12163', '12153_12166', '12153_12167', '12153_12168', '12153_12169', '12153_12170', '12153_12171', '12153_12172', '12153_12173', '12153_12174', '12153_12175', '11117_12102', '11153_12119', '11153_12122', '11153_12127', '11153_12128', '11153_12131', '11153_12135', '11153_12136', '11153_12137', '11153_12143', '11153_12144', '11153_12149', '11153_12157', '11153_12160', '11153_12165', '11153_12166', '12153_12165' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  #############################################################################
#  # V3
#  #############################################################################

#  fileNameV3Bundles = ()

#  for i in range( len( subjectV3ConnectivityMatrixDirectories ) ):

#    if os.path.exists( os.path.join( \
#                                subjectV3ConnectivityMatrixDirectories[i],
#                                'roi-to-roi-bundle-map-in-template.bundles' ) ):

#      fileNameV3Bundles += ( str( os.path.join( \
#                              subjectV3ConnectivityMatrixDirectories[i],
#                              'roi-to-roi-bundle-map-in-template.bundles' ) ), )

##  # fusion V3
#  fileNameFullV3ConnectivityTemplate = os.path.join( 
#                                       outputDirectory,
#                                       'full-v3-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : fileNameV3Bundles,
#            'fileNameOutputBundleMaps' : str( 
#                                           fileNameFullV3ConnectivityTemplate ),
#            'operatorName' : 'fusion',
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # ordering extremities
#  fileNameFullV3ConnectivityOrderedTemplate = os.path.join( 
#                               outputDirectory,
#                               'full-v3-connectivity-ordered-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV3ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                    fileNameFullV3ConnectivityOrderedTemplate ),
#            'operatorName' : 'order-extremities',
#            'scalarParameters' : 100,
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  # calculating centroids
#  fileNameFullV3ConnectivityCentroidsTemplate = os.path.join( 
#                             outputDirectory,
#                             'full-v3-connectivity-centroids-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                    fileNameFullV3ConnectivityOrderedTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                  fileNameFullV3ConnectivityCentroidsTemplate ),
#            'operatorName' : 'compute-centroids',
#            'stringParameters' : 
#                            ( "average-fiber", 
#                              "all", 
#                              "symmetric-mean-of-mean-closest-point-distance" ),
#            'scalarParameters' : ( 10000, 100, 0 ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  # extracting hippocampi clusters 17 and 53
  fileNameHippocampiV3ConnectivityTemplate = os.path.join( 
                                 outputDirectory,
                                 'hippocampi-v3-connectivity-template.bundles' )
  # ordering extremities V3
  fileNameHippocampiV3ConnectivityOrderedTemplate = os.path.join( 
                               outputDirectory,
                               'hippocampi-v3-connectivity-ordered-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                           fileNameHippocampiV3ConnectivityTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                    fileNameHippocampiV3ConnectivityOrderedTemplate ),
            'operatorName' : 'order-extremities',
            'scalarParameters' : 100,
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  # calculating centroids V3
  fileNameHippocampiV3ConnectivityCentroidsTemplate = os.path.join( 
                             outputDirectory,
                             'hippocampi-v3-connectivity-centroids-template.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                    fileNameHippocampiV3ConnectivityOrderedTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                  fileNameHippocampiV3ConnectivityCentroidsTemplate ),
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

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameFullV3ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV3ConnectivityTemplate ),
#            'operatorName' : 'select-labels',
#            'stringParameters' : ( '53_11101', '53_11102', '53_11103', '53_11105', '53_11106', '53_11107', '53_11108', '53_11109', '53_11110', '53_11111', '53_11112', '53_11113', '53_11114', '53_11115', '53_11116', '53_11117', '53_11118', '53_11119', '53_11120', '53_11121', '53_11122', '53_11123', '53_11124', '53_11125', '53_11126', '53_11127', '53_11128', '53_11129', '53_11130', '53_11131', '53_11132', '53_11133', '53_11134', '53_11135', '53_11136', '53_11137', '53_11138', '53_11139', '53_11141', '53_11143', '53_11144', '53_11145', '53_11146', '53_11147', '53_11149', '53_11151', '53_11152', '53_11153', '53_11154', '53_11155', '53_11157', '53_11158', '53_11159', '53_11161', '53_11162', '53_11164', '53_11165', '53_11166', '53_11167', '53_11168', '53_11169', '53_11170', '53_11171', '53_11172', '53_11173', '53_11174', '53_12101', '53_12102', '53_12103', '53_12104', '53_12105', '53_12106', '53_12107', '53_12108', '53_12109', '53_12110', '53_12111', '53_12112', '53_12113', '53_12114', '53_12115', '53_12116', '53_12117', '53_12118', '53_12119', '53_12120', '53_12121', '53_12122', '53_12123', '53_12124', '53_12125', '53_12126', '53_12127', '53_12128', '53_12129', '53_12130', '53_12131', '53_12132', '53_12133', '53_12134', '53_12135', '53_12136', '53_12137', '53_12138', '53_12139', '53_12140', '53_12141', '53_12143', '53_12144', '53_12145', '53_12146', '53_12147', '53_12148', '53_12149', '53_12150', '53_12151', '53_12152', '53_12153', '53_12154', '53_12155', '53_12156', '53_12157', '53_12158', '53_12159', '53_12160', '53_12161', '53_12162', '53_12163', '53_12164', '53_12165', '53_12166', '53_12167', '53_12168', '53_12169', '53_12170', '53_12171', '53_12172', '53_12173', '53_12174', '53_12175', '53_54', '53_58', '53_60', '53_80', '17_11101', '17_11102', '17_11103', '17_11104', '17_11105', '17_11106', '17_11107', '17_11108', '17_11109', '17_11110', '17_11111', '17_11112', '17_11113', '17_11114', '17_11115', '17_11116', '17_11117', '17_11118', '17_11119', '17_11120', '17_11121', '17_11122', '17_11123', '17_11124', '17_11125', '17_11126', '17_11127', '17_11128', '17_11129', '17_11130', '17_11131', '17_11132', '17_11133', '17_11134', '17_11135', '17_11136', '17_11137', '17_11138', '17_11139', '17_11140', '17_11141', '17_11143', '17_11144', '17_11145', '17_11146', '17_11147', '17_11148', '17_11149', '17_11150', '17_11151', '17_11152', '17_11153', '17_11154', '17_11155', '17_11156', '17_11157', '17_11158', '17_11159', '17_11160', '17_11161', '17_11162', '17_11163', '17_11164', '17_11165', '17_11166', '17_11167', '17_11168', '17_11169', '17_11170', '17_11171', '17_11172', '17_11173', '17_11174', '17_11175', '17_12101', '17_12102', '17_12103', '17_12105', '17_12108', '17_12109', '17_12110', '17_12111', '17_12113', '17_12114', '17_12115', '17_12116', '17_12117', '17_12118', '17_12119', '17_12120', '17_12121', '17_12122', '17_12123', '17_12124', '17_12125', '17_12127', '17_12128', '17_12129', '17_12130', '17_12131', '17_12132', '17_12133', '17_12134', '17_12135', '17_12136', '17_12137', '17_12138', '17_12139', '17_12141', '17_12143', '17_12144', '17_12145', '17_12146', '17_12147', '17_12148', '17_12149', '17_12150', '17_12151', '17_12152', '17_12153', '17_12155', '17_12157', '17_12158', '17_12159', '17_12161', '17_12162', '17_12163', '17_12164', '17_12165', '17_12166', '17_12167', '17_12168', '17_12172', '17_12173', '17_12174', '17_12175', '17_18', '17_26', '17_28', '17_47', '17_49', '17_50', '17_51', '17_52', '17_53', '17_54', '17_58', '17_60', '17_80' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : str( 
#                                           fileNameHippocampiV3ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                     fileNameHippocampiV3ConnectivityTemplate ),
#            'operatorName' : 'discard-labels',
#            'stringParameters' : ( '11117_11118', '11117_11119', '11117_11120', '11117_11121', '11117_11122', '11117_11123', '11117_11124', '11117_11125', '11117_11126', '11117_11127', '11117_11128', '11117_11129', '11117_11130', '11117_11131', '11117_11132', '11117_11133', '11117_11134', '11117_11135', '11117_11136', '11117_11137', '11117_11138', '11117_11139', '11117_11140', '11117_11141', '11117_11143', '11117_11144', '11117_11145', '11117_11146', '11117_11147', '11117_11148', '11117_11149', '11117_11150', '11117_11151', '11117_11152', '11117_11153', '11117_11154', '11117_11155', '11117_11156', '11117_11157', '11117_11158', '11117_11159', '11117_11160', '11117_11161', '11117_11162', '11117_11163', '11117_11164', '11117_11165', '11117_11166', '11117_11167', '11117_11168', '11117_11169', '11117_11170', '11117_11171', '11117_11172', '11117_11173', '11117_11174', '11117_11175', '11117_12101', '11117_12103', '11117_12105', '11117_12108', '11117_12110', '11117_12111', '11117_12113', '11117_12114', '11117_12115', '11117_12116', '11117_12117', '11117_12118', '11117_12119', '11117_12120', '11117_12121', '11117_12122', '11117_12123', '11117_12124', '11117_12125', '11117_12127', '11117_12129', '11117_12130', '11117_12131', '11117_12132', '11117_12134', '11117_12135', '11117_12138', '11117_12139', '11117_12143', '11117_12144', '11117_12145', '11117_12146', '11117_12147', '11117_12148', '11117_12150', '11117_12151', '11117_12153', '11117_12155', '11117_12157', '11117_12159', '11117_12162', '11117_12163', '11117_12164', '11117_12165', '11117_12166', '11117_12167', '11117_12172', '11117_12174', '11117_12175', '11153_11154', '11153_11155', '11153_11157', '11153_11158', '11153_11159', '11153_11161', '11153_11162', '11153_11164', '11153_11165', '11153_11166', '11153_11167', '11153_11168', '11153_11169', '11153_11170', '11153_11171', '11153_11172', '11153_11173', '11153_11174', '11153_12101', '11153_12103', '11153_12104', '11153_12105', '11153_12106', '11153_12107', '11153_12108', '11153_12109', '11153_12110', '11153_12112', '11153_12113', '11153_12114', '11153_12115', '11153_12116', '11153_12117', '11153_12118', '11153_12124', '11153_12125', '11153_12126', '11153_12129', '11153_12130', '11153_12132', '11153_12138', '11153_12139', '11153_12140', '11153_12146', '11153_12147', '11153_12148', '11153_12150', '11153_12153', '11153_12154', '11153_12155', '11153_12163', '11153_12167', '11153_12168', '11153_12169', '11153_12170', '11153_12171', '11153_12172', '11153_12174', '12117_12118', '12117_12119', '12117_12120', '12117_12121', '12117_12122', '12117_12123', '12117_12124', '12117_12125', '12117_12127', '12117_12128', '12117_12129', '12117_12130', '12117_12131', '12117_12132', '12117_12133', '12117_12134', '12117_12135', '12117_12136', '12117_12137', '12117_12138', '12117_12139', '12117_12141', '12117_12143', '12117_12144', '12117_12145', '12117_12146', '12117_12147', '12117_12148', '12117_12149', '12117_12150', '12117_12151', '12117_12152', '12117_12153', '12117_12155', '12117_12157', '12117_12158', '12117_12159', '12117_12161', '12117_12162', '12117_12163', '12117_12164', '12117_12165', '12117_12166', '12117_12167', '12117_12168', '12117_12172', '12117_12173', '12117_12174', '12117_12175', '12153_12154', '12153_12155', '12153_12156', '12153_12157', '12153_12158', '12153_12159', '12153_12160', '12153_12161', '12153_12162', '12153_12163', '12153_12166', '12153_12167', '12153_12168', '12153_12169', '12153_12170', '12153_12171', '12153_12172', '12153_12173', '12153_12174', '12153_12175', '11117_12102', '11153_12102', '11153_12131', '11153_12135', '11153_12137', '11153_12143', '11153_12149', '11153_12156', '11153_12166', '11153_12173', '12153_12164', '12153_12165' ),
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

#  #############################################################################
#  # fusionning Hippocampi V1, V2,V3
#  #############################################################################

#  fileNameHippocampiConnectivityTemplate = os.path.join( 
#                                    outputDirectory,
#                                    'hippocampi-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : ( 
#                                     fileNameHippocampiV1ConnectivityTemplate, 
#                                     fileNameHippocampiV2ConnectivityTemplate,
#                                     fileNameHippocampiV3ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                       fileNameHippocampiConnectivityTemplate ),
#            'operatorName' : 'fusion',
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  #############################################################################
  # fusionning centroids Hippocampi V1, V2,V3
  #############################################################################

  fileNameHippocampiConnectivityCentroidsTemplate = os.path.join( 
                                    outputDirectory,
                                    'hippocampi-connectivity-template-centroids.bundles' )

  gkg.executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : ( 
                                     fileNameHippocampiV1ConnectivityCentroidsTemplate, 
                                     fileNameHippocampiV2ConnectivityCentroidsTemplate,
                                     fileNameHippocampiV3ConnectivityCentroidsTemplate ),
            'fileNameOutputBundleMaps' : str( 
                                       fileNameHippocampiConnectivityCentroidsTemplate ),
            'operatorName' : 'fusion',
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


#  #############################################################################
#  # fusionning full V1, V2,V3
#  #############################################################################

#  fileNameFullConnectivityTemplate = os.path.join( 
#                                    outputDirectory,
#                                    'full-connectivity-template.bundles' )

#  gkg.executeCommand(
#      { 'algorithm' : 'DwiBundleOperator',
#        'parameters' : \
#          { 'fileNameInputBundleMaps' : ( 
#                                     fileNameFullV1ConnectivityTemplate, 
#                                     fileNameFullV2ConnectivityTemplate,
#                                     fileNameFullV3ConnectivityTemplate ),
#            'fileNameOutputBundleMaps' : str( 
#                                       fileNameFullConnectivityTemplate ),
#            'operatorName' : 'fusion',
#            'outputFormat' : 'aimsbundlemap',
#            'ascii' : False,
#            'verbose' : verbose
#          },
#        'verbose' : verbose
#      } )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
