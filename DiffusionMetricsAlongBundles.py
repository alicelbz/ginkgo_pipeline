import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def runDiffusionMetricsAlongBundles( subjectDirectoryFiberLabelling,
                                     subjectDirectoryLocalModelingDTI,
                                     subjectDirectoryLocalModelingQBI,
                                     subjectDirectoryNoddiMicrostructureField,
                                     subjectDirectoryMorphologist,
                                     outputDirectory,
                                     verbose ):
                      
  
  if ( verbose == True ):
  
    print( "COMPUTING DIFFUSION METRICS ALONG BUNDLES FROM " +
           os.path.basename( subjectDirectoryFiberLabelling ) )
    print( "-------------------------------------------------------------" )

  fileNameOrderedBundleMap = os.path.join( 
                                        subjectDirectoryFiberLabelling,
                                        'white_matter_bundles-ordered.bundles' )


  ##############################################################################
  # GFA
  ##############################################################################

  fileNameGFA = os.path.join( subjectDirectoryLocalModelingQBI, "aqbi_gfa.ima" )
  fileNameGFASpreadsheet = os.path.join( outputDirectory, "aqbi_gfa" )

  CommandFactory().executeCommand(
      { 'algorithm' : 'DwiBundleMeasure',
        'parameters' : \
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
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
          { 'fileNameBundleMap' : str( fileNameOrderedBundleMap ),
            'fileNameMeasure' : str( fileNameSTATSpreadsheet ),
            'measureNames' : 'from_volume_statistics',
            'stringParameters' : ( str( fileNameFSTAT ), "id", "none", "id" ),
            'scalarParameters' : ( 0, 0.1, 0, 1 ),
            'verbose' : verbose
          },
        'verbose' : verbose
      } )
