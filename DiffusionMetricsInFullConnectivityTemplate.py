import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runDiffusionMetricsInFullConnectivityTemplate( 
                                       subjectDirectoryFullConnectivityTemplate,
                                       subjectDirectoryLocalModelingDTI,
                                       subjectDirectoryLocalModelingQBI,
                                       subjectDirectoryNoddiMicrostructureField,
                                       subjectDirectoryMorphologist,
                                       subjectDirectoryNormalization,
                                       outputDirectory,
                                       verbose ):
                      
  
  if ( verbose == True ):
  
    print( "COMPUTING DIFFUSION METRICS In BUNDLES FROM " +
           os.path.basename( subjectDirectoryFullConnectivityTemplate ) )
    print( "-------------------------------------------------------------" )

  fileNameFullConnectivityTemplate = os.path.join( 
                                    subjectDirectoryFullConnectivityTemplate,
                                    'full-connectivity-template.bundles' )

  # resampling to subject space
  atlasToDwTrmTransform = os.path.join( subjectDirectoryNormalization,
                                        'atlas-to-dw.trm' )
  t1ToAtlasTransform = os.path.join( subjectDirectoryNormalization,
                                     't1-to-atlas.ima' )
  atlasToT1Transform = os.path.join( subjectDirectoryNormalization,
                                     'atlas-to-t1.ima' )

  fileNameFullConnectivityTemplateInSubjectSpace = os.path.join( 
                        outputDirectory,
                        'full-connectivity-template-in-dw-space.bundles' )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleOperator',
        'parameters' : \
          { 'fileNameInputBundleMaps' : str( 
                                       fileNameFullConnectivityTemplate ),
            'fileNameOutputBundleMaps' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'operatorName' : 'transform3d',
            'stringParameters' : ( atlasToDwTrmTransform, 
                                   atlasToT1Transform, 
                                   t1ToAtlasTransform ),
            'outputFormat' : 'aimsbundlemap',
            'ascii' : False,
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # GFA
  ##############################################################################

  fileNameGFA = os.path.join( subjectDirectoryLocalModelingQBI, "aqbi_gfa.ima" )
  fileNameGFASpreadsheet = os.path.join( outputDirectory, "aqbi_gfa" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameGFASpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameGFA ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # FA
  ##############################################################################

  fileNameFA = os.path.join( subjectDirectoryLocalModelingDTI, "dti_fa.ima" )
  fileNameFASpreadsheet = os.path.join( outputDirectory, "dti_fa" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameFASpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameFA ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # MD
  ##############################################################################

  fileNameMD = os.path.join( subjectDirectoryLocalModelingDTI, "dti_adc.ima" )
  fileNameMDSpreadsheet = os.path.join( outputDirectory, "dti_adc" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameMDSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameMD ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # PARALLEL DIFFUSIVITY
  ##############################################################################

  fileNameAD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_parallel_diffusivity.ima" )
  fileNameADSpreadsheet = os.path.join( outputDirectory, 
                                        "dti_parallel_diffusivity" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameADSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameAD ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  ##############################################################################
  # TRANSVERSE DIFFUSIVITY
  ##############################################################################

  fileNameRD = os.path.join( subjectDirectoryLocalModelingDTI, 
                             "dti_transverse_diffusivity.ima" )
  fileNameRDSpreadsheet = os.path.join( outputDirectory, 
                                        "dti_transverse_diffusivity" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameRDSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameRD ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

  ##############################################################################
  # INTRACELLULAR FRACTION
  ##############################################################################

  fileNameFIntra = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                                 "intracellular_fraction.ima" )
  fileNameFIntraSpreadsheet = os.path.join( outputDirectory, 
                                            "intracellular_fraction" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameFIntraSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameFIntra ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # ORIENTATION DISPERSION INDEX
  ##############################################################################

  fileNameODI = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                              "orientation_dispersion.ima" )
  fileNameODISpreadsheet = os.path.join( outputDirectory, "odi" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameODISpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameODI ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # ISOTROPIC FRACTION
  ##############################################################################

  fileNameFISO = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "isotropic_fraction.ima" )
  fileNameFISOSpreadsheet = os.path.join( outputDirectory, 
                                          "isotropic_fraction" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameFISOSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameFISO ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )


  ##############################################################################
  # STATIONARY FRACTION
  ##############################################################################

  fileNameFSTAT = os.path.join( subjectDirectoryNoddiMicrostructureField, 
                               "stationary_fraction.ima" )
  fileNameSTATSpreadsheet = os.path.join( outputDirectory, 
                                          "stationary_fraction" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( 
                         fileNameFullConnectivityTemplateInSubjectSpace ),
            'fileNameMeasure' : str( fileNameSTATSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameFSTAT ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )

