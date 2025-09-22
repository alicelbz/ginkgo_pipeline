import os
import numpy as np
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import statsmodels.stats.multitest as multi

def get_mean_metric_from_file( file, bundle, metric, verbose ):

  value = 0.0
  f = open( file, 'r' )
  lines = f.readlines()
  f.close() 

  for i in range( len( lines ) ):

    if bundle == lines[ i ].split( ' ' )[ 0 ] :

      line = lines[ i ].split( ' ' )
      valueStr = line[ 6 ]
      value = float( valueStr )

      if verbose == True:

        print( metric + " moyenne du faisceau " + bundle + " : " + \
               str( value ) )

  if value == 0.0: # could not find specific bundle

    print( "Missing data for bundle " + bundle + " in file " + file )
    value = np.nan

  return value

def plot_metrics_and_stats( controlsMetric, 
                            patientsMetric, 
                            pValue,
                            pShapiroControls,
                            pShapiroPatients,
                            pLevene, 
                            pMannWithney,
                            y_min, 
                            y_max, 
                            label,
                            showPlot ):

  if len( bundleList ) >= 50 :

    numberOfColums = 6
    numberOfRows = 9

  else:

    numberOfColums = 6
    numberOfRows = 6

  fig, axes = plt.subplots( numberOfColums, 
                            numberOfRows, 
                            sharex=True, 
                            sharey=True )
  axes = axes.flatten()
  fig.set_size_inches( 13, 9 )

  for idx, feature in enumerate( bundleList ):

    sns.boxplot( data = [ np.transpose( controlsMetric )[ idx ][:],
                          np.transpose( patientsMetric )[ idx ][:] ], 
                 linewidth=2, 
                 showmeans=True, 
                 meanprops= { "marker":"*",
                              "markerfacecolor":"white", 
                              "markeredgecolor":"black" }, 
                 ax=axes[ idx ] )

    # statistical tests
    if pShapiroControls[ idx ] < 0.05 or \
       pShapiroPatients[ idx ] < 0.05 or \
       pLevene[ idx ] < 0.05:

      if pMannWithney[ idx ] < 0.001:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5 + 0.02, 
                          "###", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          fontsize = 7,
                          transform = axes[ idx ].transAxes )

      elif pMannWithney[ idx ] < 0.01:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5 + 0.02, 
                          "##", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          fontsize = 7,
                          transform = axes[ idx ].transAxes )

      elif pMannWithney[ idx ] < 0.05:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5 + 0.02, 
                          "#", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          fontsize = 7,
                          transform = axes[ idx ].transAxes )

    else:

      if pValue[ idx ] < 0.001:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5, 
                          "***", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          transform = axes[ idx ].transAxes )

      elif pValue[ idx ] < 0.01:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5, 
                          "**", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          transform = axes[ idx ].transAxes )

      elif pValue[ idx ] < 0.05:

        x1, x2 = 0.25, 0.75
        y, h = 0.8, 0.05
        axes[ idx ].plot( [ x1, x1, x2, x2 ], 
                          [ y, y + h, y + h, y ], 
                          lw = 1.5, 
                          c = "black",
                          transform = axes[ idx ].transAxes )
        axes[ idx ].text( ( x1 + x2 ) * 0.5, 
                          y + h * 0.5, 
                          "*", 
                          ha = "center", 
                          va = "bottom", 
                          color = "black",
                          transform = axes[ idx ].transAxes )

    axes[ idx ].set_title( str( feature ), fontsize=7 )
    axes[ idx ].set_xticks( [] )
    axes[ idx ].set_ylim( [ y_min, y_max ] )

    if idx % numberOfRows == 0:

      axes[ idx ].set( ylabel = label )
    
  controls_patch = mpatches.Patch( facecolor='#1f77b4', 
                                   edgecolor='black', 
                                   label='Controls' )
  patients_patch = mpatches.Patch( facecolor='#ff7f0e', 
                                   edgecolor='black', 
                                   label='Patients' )
  fig.legend( handles=[ controls_patch, patients_patch ], loc="upper right" )

  if len( bundleList ) >= 50:

    fig.suptitle( "Mean " + label + " in short WM bundles", 
                  size = 14 )

    # plt.savefig( os.path.join( bioMRICadaDirectory, 
    #                            'Statistics', 
    #                            label + '_shortBundles_right.png' ) )

    plt.savefig( os.path.join( bioMRICadaDirectory, 
                               'Statistics', 
                               label + '_shortBundles_left.png' ) )

  else:

    fig.suptitle( "Mean " + label + " in long WM bundles", 
                  size = 14 )

    plt.savefig( os.path.join( bioMRICadaDirectory, 
                               'Statistics', 
                               label + '_longBundles.png' ) )

  if showPlot == True:
    plt.show()

def student_and_fdr_correction( controlsMetric, 
                                patientsMetric, 
                                metric,
                                verbose ):

  t, p = stats.ttest_ind( controlsMetric, 
                          patientsMetric,
                          nan_policy = "omit" )

  fdr_rejected, p_corrected = multi.fdrcorrection( p )
  positiveTTestBeforeFDR = np.count_nonzero( p < 0.05 )
  positiveTTestAfterFDR = np.count_nonzero( p_corrected < 0.05 )

  if ( verbose ) :

    print( "Number of positive " + metric + " t-tests before ( " + \
           str( positiveTTestBeforeFDR ) + " ) and after ( " + \
           str( positiveTTestAfterFDR ) + " ) FDR correction" )

  return p_corrected

def mannwithney_and_fdr_correction( controlsMetric, 
                                    patientsMetric, 
                                    bundleList,
                                    metric,
                                    verbose ):

  u = np.zeros( len( bundleList ) )
  pmw = np.zeros( len( bundleList ) )

  for i in range( len( bundleList ) ):

    u[ i ], pmw[ i ] = stats.mannwhitneyu( np.transpose( controlsMetric )[ i ], 
                                           np.transpose( patientsMetric )[ i ] )

  fdrmw_rejected, pmw_corrected = multi.fdrcorrection( pmw )

  positiveTTestBeforeFDR = np.count_nonzero( pmw < 0.05 )
  positiveTTestAfterFDR = np.count_nonzero( pmw_corrected < 0.05 )

  if ( verbose ) :

    print( "Number of positive " + metric + " Mann Withney tests before ( " + \
           str( positiveTTestBeforeFDR ) + " ) and after ( " + \
           str( positiveTTestAfterFDR ) + " ) FDR correction" )

  return pmw_corrected


bundleList = ( 'lh_Or-Ins_0', 'lh_PoCi-RAC_0', 'lh_PoC-PrC_2', 'lh_SP-SM_0', 
               'lh_IT-MT_0', 'lh_CAC-PrCu_0', 'lh_CMF-PoC_0', 'lh_CMF-Op_0', 
               'lh_RMF-SF_1', 'lh_PrC-SM_0', 'lh_PoCi-SF_0', 'lh_Op-Ins_0', 
               'lh_Fu-LO_0', 'lh_IP-IT_0', 'lh_RMF-SF_0', 'lh_PoCi-PrCu_1', 
               'lh_PrC-Ins_0', 'lh_CMF-PrC_1', 'lh_CMF-RMF_0', 'lh_MOF-ST_0', 
               'lh_PoC-Ins_0', 'lh_Op-SF_0', 'lh_Tr-SF_0', 'lh_Tr-SF_1', 
               'lh_PoC-SM_1', 'lh_IP-LO_1', 'lh_MT-SM_0', 'lh_PoC-PrC_3', 
               'lh_ST-Ins_0', 'lh_MT-ST_0', 'lh_LOF-Or_0', 'lh_IP-SP_1', 
               'lh_ST-TT_0', 'lh_IC-PrCu_0', 'lh_CMF-SF_0', 'lh_Op-PrC_0', 
               'lh_IP-SM_0', 'lh_LOF-ST_0', 'lh_CMF-PrC_0', 'lh_PoC-PrC_1', 
               'lh_Tr-Ins_0', 'lh_PoCi-PrCu_0', 'lh_IP-SP_0', 'lh_SM-Ins_0', 
               'lh_IP-MT_0', 'lh_PoC-SM_0', 'lh_PoC-PrC_0', 'lh_PrC-SF_0', 
               'lh_LOF-RMF_1', 'lh_LOF-RMF_0', 'lh_RAC-SF_1' )
               
# bundleList = ( 'rh_Or-Ins_0', 'rh_PoCi-RAC_0',
#                'rh_PoC-PrC_2', 'rh_SP-SM_0', 'rh_IT-MT_1', 'rh_CAC-PrCu_0', 
#                'rh_CMF-SF_1', 'rh_Op-Tr_0', 'rh_RMF-SF_1', 'rh_PrC-SM_0', 
#                'rh_CAC-PoCi_0',  'rh_Op-Ins_0', 'rh_Fu-LO_1', 'rh_IP-IT_0', 
#                'rh_RMF-SF_0', 'rh_PoCi-PrCu_1', 'rh_PrC-Ins_0', 'rh_CMF-PrC_1', 
#                'rh_CMF-RMF_0', 'rh_MOF-ST_0', 'rh_LO-SP_0', 'rh_Op-SF_0',
#                'rh_Tr-SF_0', 'rh_Cu-Li_0', 'rh_IP-LO_0', 'rh_MT-SM_0', 
#                'rh_PoC-SP_0', 'rh_PoC-SP_1', 'rh_MT-ST_0', 'rh_LOF-MOF_0', 
#                'rh_IT-MT_2', 'rh_ST-TT_0', 'rh_IC-PrCu_0', 'rh_CMF-SF_0', 
#                'rh_Op-PrC_0', 'rh_IP-SM_0', 'rh_LOF-ST_0', 'rh_CMF-PrC_0', 
#                'rh_PoC-PrC_1', 'rh_Tr-Ins_0', 'rh_PoCi-PrCu_2', 'rh_IP-SP_0',
#                'rh_SM-Ins_0', 'rh_IP-MT_0', 'rh_PoC-SM_0', 'rh_PoC-PrC_0', 
#                'rh_PrC-SP_0', 'rh_LOF-RMF_1', 'rh_LOF-RMF_0', 'rh_RAC-SF_0' )           

bioMRICadaDirectory = os.path.join( os.sep, 'home', 'iuszynski', 'neurospin', 
                                            'biomri_cada' )
standardStudyDirectory = os.path.join( bioMRICadaDirectory, 
                                       'Database', 
                                       'StandardStudy' )

patients = ( 'et200081', 'ct200316', 'el190724', 'jd200317', 'mj200318', 
             'fb200323', 'jf200322', 'mh200351', 'no200350', 'tz200357', 
             'fg200358', 'am200359', 'jb200360', 'ts200405', 'fj200406',
             'eg210045', 'ma210046', 'bd210096', 'jj210077', 'ca210097',
             'cc210268', 'mg210548', 'ec210592', 'oe220060', 'fc220063' )

controls = ( 'fb190563', 'mm190562', 'cd190582', 'jm190583', 'sd190584',
             'gr190585', 'ab190595', 'ar190667', 'dg190666', 'kb190696', 
             'nb200324', 'vl200348', 'ml200349', 'cv210284', 'ha210336',
             'az210471', 'fr210551', 'dd210554', 'el220062', 'bp220061', 
             'ce220064' )

bundleId = 0
patientsMeanGFAInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanGFAInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanADCInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanADCInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanFAInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanFAInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanADInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanADInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanRDInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanRDInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanIFInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanIFInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanMWFInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanMWFInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanODIInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanODIInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanFISOInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanFISOInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )
patientsMeanFSTATInBundle = np.zeros( [ len( patients ), len( bundleList ) ] )
controlsMeanFSTATInBundle = np.zeros( [ len( controls ), len( bundleList ) ] )

for bundle in bundleList:

  print( "///////////////" )
  print( "/ " + bundle )
  print( "///////////////" )

  patientId = 0
  for subject in patients:

    print( "# " + subject )

    metricsAlongBundles = os.path.join( 
                                     standardStudyDirectory, 
                                     'Patients',
                                     subject,
                                     'time1',
                                     '28-DiffusionMetricsAlongShortBundlesSRD' )

    ############################################################################
    # GFA
    ############################################################################
    gfaSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'aqbi_gfa.bundlemeasure_spreadsheet' )

    patientsMeanGFAInBundle[ patientId ][ bundleId ] = \
               get_mean_metric_from_file( gfaSpreadsheet, bundle, "GFA", False )


    ############################################################################
    # ADC
    ############################################################################
    adcSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'dti_adc.bundlemeasure_spreadsheet' )

    patientsMeanADCInBundle[ patientId ][ bundleId ] = \
               get_mean_metric_from_file( adcSpreadsheet, bundle, "ADC", False )


    ############################################################################
    # FA
    ############################################################################
    faSpreadsheet = os.path.join( metricsAlongBundles, 
                                  'dti_fa.bundlemeasure_spreadsheet' )

    patientsMeanFAInBundle[ patientId ][ bundleId ] = \
                 get_mean_metric_from_file( faSpreadsheet, bundle, "FA", False )


    ############################################################################
    # PARALLEL DIFFUSIVITY
    ############################################################################
    adSpreadsheet = os.path.join( 
                          metricsAlongBundles, 
                          'dti_parallel_diffusivity.bundlemeasure_spreadsheet' )

    patientsMeanADInBundle[ patientId ][ bundleId ] = \
                 get_mean_metric_from_file( adSpreadsheet, bundle, "AD", False )


    ############################################################################
    # TRANSVERSE DIFFUSIVITY
    ############################################################################
    rdSpreadsheet = os.path.join( 
                        metricsAlongBundles, 
                        'dti_transverse_diffusivity.bundlemeasure_spreadsheet' )

    patientsMeanRDInBundle[ patientId ][ bundleId ] = \
                 get_mean_metric_from_file( rdSpreadsheet, bundle, "RD", False )


    ############################################################################
    # INTRACELLULAR FRACTION
    ############################################################################
    intraFractionSpreadsheet = os.path.join( 
                            metricsAlongBundles, 
                            'intracellular_fraction.bundlemeasure_spreadsheet' )

    patientsMeanIFInBundle[ patientId ][ bundleId ] = \
                            get_mean_metric_from_file( intraFractionSpreadsheet, 
                                                       bundle, 
                                                       "FIntra", 
                                                       False )


    ############################################################################
    # ORIENTATION DISPERION INDEX
    ############################################################################
    odiSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'odi.bundlemeasure_spreadsheet' )

    patientsMeanODIInBundle[ patientId ][ bundleId ] = \
                                      get_mean_metric_from_file( odiSpreadsheet, 
                                                                 bundle, 
                                                                 "ODI", 
                                                                 False )


    ############################################################################
    # ISOTROPIC FRACTION
    ############################################################################
    fisoSpreadsheet = os.path.join( 
                                metricsAlongBundles, 
                                'isotropic_fraction.bundlemeasure_spreadsheet' )

    patientsMeanFISOInBundle[ patientId ][ bundleId ] = \
                                      get_mean_metric_from_file( 
                                                                fisoSpreadsheet, 
                                                                bundle, 
                                                                "FISO", 
                                                                False )


    ############################################################################
    # STATIONARY FRACTION
    ############################################################################
    fstatSpreadsheet = os.path.join( 
                               metricsAlongBundles, 
                               'stationary_fraction.bundlemeasure_spreadsheet' )

    patientsMeanFSTATInBundle[ patientId ][ bundleId ] = \
                                      get_mean_metric_from_file( 
                                                               fstatSpreadsheet, 
                                                               bundle, 
                                                               "FSTAT", 
                                                               False )


    ############################################################################
    # MYELIN WATER FRACTION
    ############################################################################
    mwFractionSpreadsheet = os.path.join( metricsAlongBundles, 
                                          'mwf.bundlemeasure_spreadsheet' )

    patientsMeanMWFInBundle[ patientId ][ bundleId ] = \
        get_mean_metric_from_file( mwFractionSpreadsheet, bundle, "MWF", False )


    patientId += 1

  controlId = 0
  for subject in controls:

    print( "# " + subject )

    metricsAlongBundles = os.path.join( 
                                     standardStudyDirectory, 
                                     'Controls',
                                     subject,
                                     'time1',
                                     '28-DiffusionMetricsAlongShortBundlesSRD' )

    ############################################################################
    # GFA
    ############################################################################
    gfaSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'aqbi_gfa.bundlemeasure_spreadsheet' )

    controlsMeanGFAInBundle[ controlId ][ bundleId ] = \
               get_mean_metric_from_file( gfaSpreadsheet, bundle, "GFA", False )


    ############################################################################
    # ADC
    ############################################################################
    adcSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'dti_adc.bundlemeasure_spreadsheet' )

    controlsMeanADCInBundle[ controlId ][ bundleId ] = \
               get_mean_metric_from_file( adcSpreadsheet, bundle, "ADC", False )


    ############################################################################
    # FA
    ############################################################################
    faSpreadsheet = os.path.join( metricsAlongBundles, 
                                  'dti_fa.bundlemeasure_spreadsheet' )

    controlsMeanFAInBundle[ controlId ][ bundleId ] = \
                 get_mean_metric_from_file( faSpreadsheet, bundle, "FA", False )


    ############################################################################
    # AD
    ############################################################################
    adSpreadsheet = os.path.join( 
                          metricsAlongBundles, 
                          'dti_parallel_diffusivity.bundlemeasure_spreadsheet' )

    controlsMeanADInBundle[ controlId ][ bundleId ] = \
                 get_mean_metric_from_file( adSpreadsheet, bundle, "AD", False )


    ############################################################################
    # RD
    ############################################################################
    rdSpreadsheet = os.path.join( 
                        metricsAlongBundles, 
                        'dti_transverse_diffusivity.bundlemeasure_spreadsheet' )

    controlsMeanRDInBundle[ controlId ][ bundleId ] = \
                 get_mean_metric_from_file( rdSpreadsheet, bundle, "RD", False )


    ############################################################################
    # INTRACELLULAR FRACTION
    ############################################################################
    intraFractionSpreadsheet = os.path.join( 
                            metricsAlongBundles, 
                            'intracellular_fraction.bundlemeasure_spreadsheet' )

    controlsMeanIFInBundle[ controlId ][ bundleId ] = \
                            get_mean_metric_from_file( intraFractionSpreadsheet, 
                                                       bundle, 
                                                       "FIntra", 
                                                       False )


    ############################################################################
    # ORIENTATION DISPERSION INDEX
    ############################################################################
    odiSpreadsheet = os.path.join( metricsAlongBundles, 
                                   'odi.bundlemeasure_spreadsheet' )

    controlsMeanODIInBundle[ controlId ][ bundleId ] = \
                                      get_mean_metric_from_file( odiSpreadsheet, 
                                                                 bundle, 
                                                                 "ODI", 
                                                                 False )


    ############################################################################
    # ISOTROPIC FRACTION
    ############################################################################
    fisoSpreadsheet = os.path.join( 
                                metricsAlongBundles, 
                                'isotropic_fraction.bundlemeasure_spreadsheet' )

    controlsMeanFISOInBundle[ controlId ][ bundleId ] = \
                                      get_mean_metric_from_file( 
                                                                fisoSpreadsheet, 
                                                                bundle, 
                                                                "FISO", 
                                                                False )


    ############################################################################
    # STATIONARY FRACTION
    ############################################################################
    fstatSpreadsheet = os.path.join( 
                               metricsAlongBundles, 
                               'stationary_fraction.bundlemeasure_spreadsheet' )

    controlsMeanFSTATInBundle[ controlId ][ bundleId ] = \
                                      get_mean_metric_from_file( 
                                                               fstatSpreadsheet, 
                                                               bundle, 
                                                               "FSTAT", 
                                                               False )


    ############################################################################
    # MYELIN WATER FRACTION
    ############################################################################
    mwFractionSpreadsheet = os.path.join( metricsAlongBundles, 
                                          'mwf.bundlemeasure_spreadsheet' )

    controlsMeanMWFInBundle[ controlId ][ bundleId ] = \
        get_mean_metric_from_file( mwFractionSpreadsheet, bundle, "MWF", False )


    controlId += 1

  bundleId += 1


################################################################################
# Shapiro (normality), Levene (homogeneity of variance) and Student Tests
#  Perform Mann Withney if t test not possible
################################################################################

stat_gfa_controls = np.zeros( len( bundleList ) )
stat_adc_controls = np.zeros( len( bundleList ) )
stat_fa_controls = np.zeros( len( bundleList ) )
stat_ad_controls = np.zeros( len( bundleList ) )
stat_rd_controls = np.zeros( len( bundleList ) )
stat_if_controls = np.zeros( len( bundleList ) )
stat_mwf_controls = np.zeros( len( bundleList ) )
stat_odi_controls = np.zeros( len( bundleList ) )
stat_fiso_controls = np.zeros( len( bundleList ) )
stat_fstat_controls = np.zeros( len( bundleList ) )

stat_gfa_patients = np.zeros( len( bundleList ) )
stat_adc_patients = np.zeros( len( bundleList ) )
stat_fa_patients = np.zeros( len( bundleList ) )
stat_ad_patients = np.zeros( len( bundleList ) )
stat_rd_patients = np.zeros( len( bundleList ) )
stat_if_patients = np.zeros( len( bundleList ) )
stat_mwf_patients = np.zeros( len( bundleList ) )
stat_odi_patients = np.zeros( len( bundleList ) )
stat_fiso_patients = np.zeros( len( bundleList ) )
stat_fstat_patients = np.zeros( len( bundleList ) )

ps_gfa_controls = np.zeros( len( bundleList ) )
ps_adc_controls = np.zeros( len( bundleList ) )
ps_fa_controls = np.zeros( len( bundleList ) )
ps_ad_controls = np.zeros( len( bundleList ) )
ps_rd_controls = np.zeros( len( bundleList ) )
ps_if_controls = np.zeros( len( bundleList ) )
ps_mwf_controls = np.zeros( len( bundleList ) )
ps_odi_controls = np.zeros( len( bundleList ) )
ps_fiso_controls = np.zeros( len( bundleList ) )
ps_fstat_controls = np.zeros( len( bundleList ) )

ps_gfa_patients = np.zeros( len( bundleList ) )
ps_adc_patients = np.zeros( len( bundleList ) )
ps_fa_patients = np.zeros( len( bundleList ) )
ps_ad_patients = np.zeros( len( bundleList ) )
ps_rd_patients = np.zeros( len( bundleList ) )
ps_if_patients = np.zeros( len( bundleList ) )
ps_mwf_patients = np.zeros( len( bundleList ) )
ps_odi_patients = np.zeros( len( bundleList ) )
ps_fiso_patients = np.zeros( len( bundleList ) )
ps_fstat_patients = np.zeros( len( bundleList ) )

w_gfa = np.zeros( len( bundleList ) )
w_adc = np.zeros( len( bundleList ) )
w_fa = np.zeros( len( bundleList ) )
w_ad = np.zeros( len( bundleList ) )
w_rd = np.zeros( len( bundleList ) )
w_if = np.zeros( len( bundleList ) )
w_mwf = np.zeros( len( bundleList ) )
w_odi = np.zeros( len( bundleList ) )
w_fiso = np.zeros( len( bundleList ) )
w_fstat = np.zeros( len( bundleList ) )

pl_gfa = np.zeros( len( bundleList ) )
pl_adc = np.zeros( len( bundleList ) )
pl_fa = np.zeros( len( bundleList ) )
pl_ad = np.zeros( len( bundleList ) )
pl_rd = np.zeros( len( bundleList ) )
pl_if = np.zeros( len( bundleList ) )
pl_mwf = np.zeros( len( bundleList ) )
pl_odi = np.zeros( len( bundleList ) )
pl_fiso = np.zeros( len( bundleList ) )
pl_fstat = np.zeros( len( bundleList ) )

for i in range( len( bundleList ) ):

  print( ">> " + bundleList[ i ] )
  # Shapiro
  stat_gfa_controls[ i ], ps_gfa_controls[ i ] = stats.shapiro( 
                                  np.transpose( controlsMeanGFAInBundle )[ i ] )

  stat_gfa_patients[ i ], ps_gfa_patients[ i ] = stats.shapiro( 
                                  np.transpose( patientsMeanGFAInBundle )[ i ] )

  stat_adc_controls[ i ], ps_adc_controls[ i ] = stats.shapiro( 
                                  np.transpose( controlsMeanADCInBundle )[ i ] )

  stat_adc_patients[ i ], ps_adc_patients[ i ] = stats.shapiro( 
                                  np.transpose( patientsMeanADCInBundle )[ i ] )

  stat_fa_controls[ i ], ps_fa_controls[ i ] = stats.shapiro( 
                                   np.transpose( controlsMeanFAInBundle )[ i ] )

  stat_fa_patients[ i ], ps_fa_patients[ i ] = stats.shapiro( 
                                   np.transpose( patientsMeanFAInBundle )[ i ] )

  stat_ad_controls[ i ], ps_ad_controls[ i ] = stats.shapiro( 
                                   np.transpose( controlsMeanADInBundle )[ i ] )

  stat_ad_patients[ i ], ps_ad_patients[ i ] = stats.shapiro( 
                                   np.transpose( patientsMeanADInBundle )[ i ] )

  stat_rd_controls[ i ], ps_rd_controls[ i ] = stats.shapiro( 
                                   np.transpose( controlsMeanRDInBundle )[ i ] )

  stat_rd_patients[ i ], ps_rd_patients[ i ] = stats.shapiro( 
                                   np.transpose( patientsMeanRDInBundle )[ i ] )

  stat_if_controls[ i ], ps_if_controls[ i ] = stats.shapiro( 
                                   np.transpose( controlsMeanIFInBundle )[ i ] )

  stat_if_patients[ i ], ps_if_patients[ i ] = stats.shapiro( 
                                   np.transpose( patientsMeanIFInBundle )[ i ] )

  stat_mwf_controls[ i ], ps_mwf_controls[ i ] = stats.shapiro( 
                                  np.transpose( controlsMeanMWFInBundle )[ i ] )

  stat_mwf_patients[ i ], ps_mwf_patients[ i ] = stats.shapiro( 
                                  np.transpose( patientsMeanMWFInBundle )[ i ] )

  stat_odi_controls[ i ], ps_odi_controls[ i ] = stats.shapiro( 
                                  np.transpose( controlsMeanODIInBundle )[ i ] )

  stat_odi_patients[ i ], ps_odi_patients[ i ] = stats.shapiro( 
                                  np.transpose( patientsMeanODIInBundle )[ i ] )

  stat_fiso_controls[ i ], ps_fiso_controls[ i ] = stats.shapiro( 
                                 np.transpose( controlsMeanFISOInBundle )[ i ] )

  stat_fiso_patients[ i ], ps_fiso_patients[ i ] = stats.shapiro( 
                                 np.transpose( patientsMeanFISOInBundle )[ i ] )

  stat_fstat_controls[ i ], ps_fstat_controls[ i ] = stats.shapiro( 
                                np.transpose( controlsMeanFSTATInBundle )[ i ] )

  stat_fstat_patients[ i ], ps_fstat_patients[ i ] = stats.shapiro( 
                                 np.transpose( patientsMeanFSTATInBundle )[ i ] )

  # Levene
  w_gfa[ i ], pl_gfa[ i ] = stats.levene( 
                                   np.transpose( controlsMeanGFAInBundle )[ i ], 
                                   np.transpose( patientsMeanGFAInBundle )[ i ], 
                                   center = "mean" )
  w_adc[ i ], pl_adc[ i ] = stats.levene( 
                                   np.transpose( controlsMeanADCInBundle )[ i ],             
                                   np.transpose( patientsMeanADCInBundle )[ i ], 
                                   center = "mean" )
  w_fa[ i ], pl_fa[ i ] = stats.levene( 
                                    np.transpose( controlsMeanFAInBundle )[ i ], 
                                    np.transpose( patientsMeanFAInBundle )[ i ], 
                                    center = "mean" )
  w_ad[ i ], pl_ad[ i ] = stats.levene( 
                                    np.transpose( controlsMeanADInBundle )[ i ], 
                                    np.transpose( patientsMeanADInBundle )[ i ], 
                                    center = "mean" )
  w_rd[ i ], pl_rd[ i ] = stats.levene( 
                                    np.transpose( controlsMeanRDInBundle )[ i ], 
                                    np.transpose( patientsMeanRDInBundle )[ i ], 
                                    center = "mean" )
  w_if[ i ], pl_if[ i ] = stats.levene( 
                                    np.transpose( controlsMeanIFInBundle )[ i ], 
                                    np.transpose( patientsMeanIFInBundle )[ i ], 
                                    center = "mean" )
  w_mwf[ i ], pl_mwf[ i ] = stats.levene( 
                                   np.transpose( controlsMeanMWFInBundle )[ i ], 
                                   np.transpose( patientsMeanMWFInBundle )[ i ], 
                                   center = "mean" )
  w_odi[ i ], pl_odi[ i ] = stats.levene( 
                                   np.transpose( controlsMeanODIInBundle )[ i ], 
                                   np.transpose( patientsMeanODIInBundle )[ i ], 
                                   center = "mean" )
  w_fiso[ i ], pl_fiso[ i ] = stats.levene( 
                                  np.transpose( controlsMeanFISOInBundle )[ i ], 
                                  np.transpose( patientsMeanFISOInBundle )[ i ], 
                                  center = "mean" )
  w_fstat[ i ], pl_fstat[ i ] = stats.levene( 
                                 np.transpose( controlsMeanFSTATInBundle )[ i ], 
                                 np.transpose( patientsMeanFSTATInBundle )[ i ], 
                                 center = "mean" )

# Mann Withney
pmw_gfa_corrected = mannwithney_and_fdr_correction( controlsMeanGFAInBundle, 
                                                    patientsMeanGFAInBundle, 
                                                    bundleList,
                                                    "GFA",
                                                    True )

pmw_adc_corrected = mannwithney_and_fdr_correction( controlsMeanADCInBundle, 
                                                    patientsMeanADCInBundle, 
                                                    bundleList,
                                                    "ADC",
                                                    True )

pmw_fa_corrected = mannwithney_and_fdr_correction( controlsMeanFAInBundle, 
                                                   patientsMeanFAInBundle, 
                                                   bundleList,
                                                   "FA",
                                                   True )

pmw_ad_corrected = mannwithney_and_fdr_correction( controlsMeanADInBundle, 
                                                   patientsMeanADInBundle, 
                                                   bundleList,
                                                   "AD",
                                                   True )

pmw_rd_corrected = mannwithney_and_fdr_correction( controlsMeanRDInBundle, 
                                                   patientsMeanRDInBundle, 
                                                   bundleList,
                                                   "RD",
                                                   True )

pmw_if_corrected = mannwithney_and_fdr_correction( controlsMeanIFInBundle, 
                                                   patientsMeanIFInBundle, 
                                                   bundleList,
                                                   "F Intra",
                                                   True )

pmw_mwf_corrected = mannwithney_and_fdr_correction( controlsMeanMWFInBundle, 
                                                    patientsMeanMWFInBundle, 
                                                    bundleList,
                                                    "MWF",
                                                    True )

pmw_odi_corrected = mannwithney_and_fdr_correction( controlsMeanODIInBundle, 
                                                    patientsMeanODIInBundle, 
                                                    bundleList,
                                                    "ODI",
                                                    True )

pmw_fiso_corrected = mannwithney_and_fdr_correction( controlsMeanFISOInBundle, 
                                                     patientsMeanFISOInBundle, 
                                                     bundleList,
                                                     "F ISO",
                                                     True )

pmw_fstat_corrected = mannwithney_and_fdr_correction( controlsMeanFSTATInBundle, 
                                                      patientsMeanFSTATInBundle, 
                                                      bundleList,
                                                      "F STAT",
                                                      True )

# Student
p_gfa_corrected = student_and_fdr_correction( controlsMeanGFAInBundle, 
                                              patientsMeanGFAInBundle, 
                                              "GFA",
                                              True )

p_adc_corrected = student_and_fdr_correction( controlsMeanADCInBundle, 
                                              patientsMeanADCInBundle, 
                                              "ADC",
                                              True )

p_fa_corrected = student_and_fdr_correction( controlsMeanFAInBundle, 
                                             patientsMeanFAInBundle, 
                                             "FA",
                                             True )

p_ad_corrected = student_and_fdr_correction( controlsMeanADInBundle, 
                                             patientsMeanADInBundle, 
                                             "AD",
                                             True )

p_rd_corrected = student_and_fdr_correction( controlsMeanRDInBundle, 
                                              patientsMeanRDInBundle, 
                                              "RD",
                                              True )

p_if_corrected = student_and_fdr_correction( controlsMeanIFInBundle, 
                                              patientsMeanIFInBundle, 
                                              "F Intra",
                                              True )

p_mwf_corrected = student_and_fdr_correction( controlsMeanMWFInBundle, 
                                              patientsMeanMWFInBundle, 
                                              "MWF",
                                              True )

p_odi_corrected = student_and_fdr_correction( controlsMeanODIInBundle, 
                                              patientsMeanODIInBundle, 
                                              "ODI",
                                              True )

p_fiso_corrected = student_and_fdr_correction( controlsMeanFISOInBundle, 
                                              patientsMeanFISOInBundle, 
                                              "F ISO",
                                              True )

p_fstat_corrected = student_and_fdr_correction( controlsMeanFSTATInBundle, 
                                              patientsMeanFSTATInBundle, 
                                              "F STAT",
                                              True )


################################################################################
# Boxplots
################################################################################

plot_metrics_and_stats( controlsMeanGFAInBundle, 
                        patientsMeanGFAInBundle, 
                        p_gfa_corrected,
                        ps_gfa_controls,
                        ps_gfa_patients,
                        pl_gfa, 
                        pmw_gfa_corrected,
                        0.03, 
                        0.10, 
                        "GFA",
                        True )

plot_metrics_and_stats( controlsMeanADCInBundle, 
                        patientsMeanADCInBundle, 
                        p_adc_corrected, 
                        ps_adc_controls,
                        ps_adc_patients,
                        pl_adc, 
                        pmw_adc_corrected,
                        0.5e-9, 
                        1.5e-9, 
                        "ADC",
                        True )

plot_metrics_and_stats( controlsMeanFAInBundle, 
                        patientsMeanFAInBundle, 
                        p_fa_corrected, 
                        ps_fa_controls,
                        ps_fa_patients,
                        pl_fa, 
                        pmw_fa_corrected,
                        0.1, 
                        0.7, 
                        "FA",
                        True )

plot_metrics_and_stats( controlsMeanADInBundle, 
                        patientsMeanADInBundle, 
                        p_ad_corrected, 
                        ps_ad_controls,
                        ps_ad_patients,
                        pl_ad, 
                        pmw_ad_corrected,
                        0.7e-9, 
                        1.7e-9, 
                        "AD",
                        True )

plot_metrics_and_stats( controlsMeanRDInBundle, 
                        patientsMeanRDInBundle, 
                        p_rd_corrected, 
                        ps_rd_controls,
                        ps_rd_patients,
                        pl_rd, 
                        pmw_rd_corrected,
                        0.3e-9, 
                        1.3e-9, 
                        "RD",
                        True )

plot_metrics_and_stats( controlsMeanIFInBundle, 
                        patientsMeanIFInBundle, 
                        p_if_corrected, 
                        ps_if_controls,
                        ps_if_patients,
                        pl_if, 
                        pmw_if_corrected,
                        0.1, 
                        0.7, 
                        "F Intra",
                        True )

plot_metrics_and_stats( controlsMeanMWFInBundle, 
                        patientsMeanMWFInBundle, 
                        p_mwf_corrected, 
                        ps_mwf_controls,
                        ps_mwf_patients,
                        pl_mwf, 
                        pmw_mwf_corrected,
                        0.04, 
                        0.35, 
                        "MWF",
                        True )

plot_metrics_and_stats( controlsMeanODIInBundle, 
                        patientsMeanODIInBundle, 
                        p_odi_corrected, 
                        ps_odi_controls,
                        ps_odi_patients,
                        pl_odi, 
                        pmw_odi_corrected,
                        0.2, 
                        0.6, 
                        "ODI",
                        True )

plot_metrics_and_stats( controlsMeanFISOInBundle, 
                        patientsMeanFISOInBundle, 
                        p_fiso_corrected, 
                        ps_fiso_controls,
                        ps_fiso_patients,
                        pl_fiso, 
                        pmw_fiso_corrected,
                        -0.01, 
                        0.16, 
                        "FISO",
                        True )

plot_metrics_and_stats( controlsMeanFSTATInBundle, 
                        patientsMeanFSTATInBundle, 
                        p_fstat_corrected, 
                        ps_fstat_controls,
                        ps_fstat_patients,
                        pl_fstat, 
                        pmw_fstat_corrected,
                        -0.01, 
                        0.07, 
                        "FSTAT",
                        True )