import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg
import shutil

from CopyFileDirectoryRm import *

def runFreeSurferParcellation( subjectDirectoryMorphologist,
                               subjectName,
                               outputDirectory,
                               verbose ):
  #import os
                      
  
  if ( verbose == True ):
  
    print( "FREESURFER PARCELLATION" )
    print( "-------------------------------------------------------------" )

  #- NIFTI convertion - - - - - - - - - - - - - - - - - - - - - - - - - 

  outputFreesurfer01InputDirectory = makeDirectory( outputDirectory,
                                                    "01-Input" )

  fileNameGisT1S16 = os.path.join( subjectDirectoryMorphologist,
                                   't1-S16.ima' )
  fileNameNiftiT1S16 = os.path.join( outputFreesurfer01InputDirectory,
                                     't1_S16.nii' )

  gkg.executeCommand(
    { 'algorithm' : 'Gis2NiftiConverter',
      'parameters' : \
      { 'fileNameIn' : str( fileNameGisT1S16 ),
        'fileNameOut' : str( fileNameNiftiT1S16 ),
        'verbose' : verbose
      },
      'verbose' : verbose
    } )

  removeMinf( fileNameNiftiT1S16 )

  #- recon-all - - - -- - - - - - - - - - - - - - - - - - - - - - - - - 

  fs_subj_dir = os.environ.get('SUBJECTS_DIR')
  #outputFreesurfer02ReconAll = makeDirectory( outputDirectory, '02-ReconAll' )
  outputFreesurfer02ReconAll = os.path.join( outputDirectory, '02-ReconAll' )
  outputFreesurfer02ReconAllLin = makeDirectory( fs_subj_dir, '02-ReconAll' )
  # skip = True
  # if not skip:
  if not os.path.isfile(os.path.join(outputFreesurfer02ReconAll, subjectName, 'label', 'BA_exvivo.thresh.ctab')):
      shutil.rmtree(outputFreesurfer02ReconAll, ignore_errors=True)

      command = 'recon-all -all' + \
                ' -subjid ' + subjectName + \
                ' -i ' + fileNameNiftiT1S16 + \
                ' -sd ' + outputFreesurfer02ReconAllLin
      print( command )
      os.system( command )

      shutil.copytree(os.path.join(outputFreesurfer02ReconAllLin, subjectName), os.path.join(outputFreesurfer02ReconAll, subjectName), symlinks=False, ignore=None, ignore_dangling_symlinks=False, dirs_exist_ok=False)
      shutil.rmtree(os.path.join(outputFreesurfer02ReconAllLin, subjectName), ignore_errors=True)

  #- hippocampal subfield parcellation  - - - - - - - - - - - -
  if not os.path.isfile(os.path.join(outputFreesurfer02ReconAll, subjectName, 'mri', 'rh.hippoAmygLabels-T1.v21.mgz')):
      command = 'segmentHA_T1.sh ' + subjectName + ' ' + outputFreesurfer02ReconAll
      print(command)
      os.system(command)
  else:
      print(f"SKIPPED: hippocampal subfield parcellation for subject {subjectName}")

  #- resampling to icosahedron of order 7 mesh  - - - - - - - - - - - - 

  outputFreesurfer03ToIcoOrder7 = makeDirectory( outputDirectory,
                                                 '03-ToIcosahedronOrder7' )
  
  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --sval-xyz ' + 'pial' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'lh.pial' ) + \
            ' --tval-xyz ' + os.path.join( outputFreesurfer02ReconAll,
                                           subjectName,
                                           "mri",
                                           "orig.mgz" ) + \
            ' --hemi ' + 'lh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --sval-xyz ' + 'white' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'lh.white' ) + \
            ' --tval-xyz ' + os.path.join( outputFreesurfer02ReconAll,
                                           subjectName,
                                           "mri",
                                           "orig.mgz" ) + \
            ' --hemi ' + 'lh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --sval-xyz ' + 'pial' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'rh.pial' ) + \
            ' --tval-xyz ' + os.path.join( outputFreesurfer02ReconAll,
                                           subjectName,
                                           "mri",
                                           "orig.mgz" ) + \
            ' --hemi ' + 'rh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --sval-xyz ' + 'white' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'rh.white' ) + \
            ' --tval-xyz ' + os.path.join( outputFreesurfer02ReconAll,
                                           subjectName,
                                           "mri",
                                           "orig.mgz" ) + \
            ' --hemi ' + 'rh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'lh.aparc.a2009s.annot' ) + \
            ' --sval-annot ' + os.path.join( outputFreesurfer02ReconAll,
                                             subjectName,
                                             'label',
                                             'lh.aparc.a2009s.annot' )+ \
            ' --hemi ' + 'lh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  command = 'export SUBJECTS_DIR=' + outputFreesurfer02ReconAll + \
            ';mri_surf2surf' + \
            ' --srcsubject ' + subjectName + \
            ' --trgsubject ico ' + \
            ' --trgicoorder 7 ' + \
            ' --tval ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                       'rh.aparc.a2009s.annot' ) + \
            ' --sval-annot ' + os.path.join( outputFreesurfer02ReconAll,
                                             subjectName,
                                             'label',
                                             'rh.aparc.a2009s.annot' ) +\
            ' --hemi ' + 'rh' + \
            ' --s ' + subjectName
  print( command )
  os.system( command )

  #- converting to GIFTI and NIFTI formats - - - - - - - - - - - - - - -

  outputFreesurfer04GiftiAndNifti = makeDirectory( outputDirectory,
                                                   '04-GiftiAndNifti' )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'aseg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'aseg.nii.gz' ) + ' ' + \
            ' -odt int'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'aparc+aseg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'aparc+aseg.nii.gz' ) + ' ' + \
            ' -odt int'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'aparc.a2009s+aseg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'aparc.a2009s+aseg.nii.gz' ) + ' ' + \
            ' -odt int'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'wmparc.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'wmparc.nii.gz' ) + ' ' + \
            ' -odt int'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'lh.hippoAmygLabels-T1.v21.FS60.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.hippoAmygLabels-T1.v21.FS60.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'rh.hippoAmygLabels-T1.v21.FS60.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.hippoAmygLabels-T1.v21.FS60.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'lh.hippoAmygLabels-T1.v21.HBT.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.hippoAmygLabels-T1.v21.HBT.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'rh.hippoAmygLabels-T1.v21.HBT.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.hippoAmygLabels-T1.v21.HBT.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'lh.hippoAmygLabels-T1.v21.CA.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.hippoAmygLabels-T1.v21.CA.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mri_convert' + \
            ' --resample_type nearest ' + \
            ' --reslice_like ' + os.path.join( outputFreesurfer02ReconAll,
                                               subjectName,
                                               'mri',
                                               'rawavg.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer02ReconAll,
                          subjectName,
                          'mri',
                          'rh.hippoAmygLabels-T1.v21.CA.mgz' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.hippoAmygLabels-T1.v21.CA.nii.gz' ) + ' ' + \
            ' -odt int -ns 1'
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'lh.pial' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.pial.gii' )
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'lh.white' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.white.gii' )
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'rh.pial' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.pial.gii' )
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'rh.white' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.white.gii' )
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            ' --annot ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                        'lh.aparc.a2009s.annot' ) + ' ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'lh.pial' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'lh.aparc.a2009s.annot.gii' )
  print( command )
  os.system( command )

  command = 'mris_convert ' + \
            ' --annot ' + os.path.join( outputFreesurfer03ToIcoOrder7,
                                        'rh.aparc.a2009s.annot' ) + ' ' + \
            os.path.join( outputFreesurfer03ToIcoOrder7,
                          'rh.pial' ) + ' ' + \
            os.path.join( outputFreesurfer04GiftiAndNifti,
                          'rh.aparc.a2009s.annot.gii' )
  print( command )
  os.system( command )

  #- results into subject native space and GIS/*.mesh/*.tex format - - -

  outputFreesurfer05ToNativeSpace = makeDirectory( outputDirectory,
                                                   '05-ToNativeSpace' )

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'aseg.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'aseg.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  # removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'aseg.ima' ) )

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'aparc+aseg.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'aparc+aseg.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 
                            'aparc+aseg.ima' ) )

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'aparc.a2009s+aseg.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'aparc.a2009s+aseg.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 
                            'aparc.a2009s+aseg.ima' ) )

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'wmparc.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'wmparc.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'wmparc.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'wmparc.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'wmparc-S16.ima' ) 
  print( command )
  os.system( command )


  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'lh.hippoAmygLabels-T1.v21.FS60.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.FS60.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.hippoAmygLabels-T1.v21.FS60.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.FS60.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.FS60-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsLHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_lh_FS60_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.FS60-S16.ima' )  + ' ' + \
            ' > ' + fileNameHippSubFieldsLHVolumeTxt
  print( command )
  os.system( command ) 

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'rh.hippoAmygLabels-T1.v21.FS60.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.FS60.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.hippoAmygLabels-T1.v21.FS60.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.FS60.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.FS60-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsRHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_rh_FS60_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.FS60-S16.ima' )  + ' ' + \
            ' > ' + fileNameHippSubFieldsRHVolumeTxt
  print( command )
  os.system( command ) 

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'lh.hippoAmygLabels-T1.v21.HBT.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.HBT.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.hippoAmygLabels-T1.v21.HBT.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.HBT.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.HBT-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsLHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_lh_HBT_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.HBT-S16.ima' )  + ' ' + \
            ' > ' + fileNameHippSubFieldsLHVolumeTxt
  print( command )
  os.system( command ) 

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'rh.hippoAmygLabels-T1.v21.HBT.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.HBT.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.hippoAmygLabels-T1.v21.HBT.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.HBT.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.HBT-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsRHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_rh_HBT_volume.txt' )

  command = 'AimsRoiFeatures' + \
              ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                                 'rh.hippoAmygLabels-T1.v21.HBT-S16.ima' )  + ' ' + \
              ' > ' + fileNameHippSubFieldsRHVolumeTxt
  print( command )
  os.system( command ) 

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'lh.hippoAmygLabels-T1.v21.CA.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.CA.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.hippoAmygLabels-T1.v21.CA.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.CA.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.CA-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsLHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_lh_CA_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.hippoAmygLabels-T1.v21.CA-S16.ima' )  + ' ' + \
            ' > ' + fileNameHippSubFieldsLHVolumeTxt
  print( command )
  os.system( command ) 

  gkg.executeCommand(
      { 'algorithm' : 'Nifti2GisConverter',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer04GiftiAndNifti,
                                              'rh.hippoAmygLabels-T1.v21.CA.nii.gz' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.CA.ima' ) ),
            'outputFormat' : 'gis',
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.hippoAmygLabels-T1.v21.CA.ima' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.CA.ima' ) + ' ' + \
            ' -t S16 '  + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.CA-S16.ima' )
  print( command )
  os.system( command )

  fileNameHippSubFieldsRHVolumeTxt = os.path.join( outputDirectory, 'hippocampus_subfields_rh_CA_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.hippoAmygLabels-T1.v21.CA-S16.ima' )  + ' ' + \
            ' > ' + fileNameHippSubFieldsRHVolumeTxt
  print( command )
  os.system( command ) 

  command = 'AimsSelectLabel ' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'wmparc-S16.ima' ) + ' ' + \
            ' -l 17 53' + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'hippocampus.ima' ) 
  print( command )
  os.system( command )

  fileNameBrainVolumeTxt = os.path.join( outputDirectory, 'hippocampus_volume.txt' )

  command = 'AimsRoiFeatures' + \
            ' -i ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                               'hippocampus.ima' )  + ' ' + \
            ' > ' + fileNameBrainVolumeTxt
  print( command )
  os.system( command ) 


  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'lh.pial.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'lh.pial.mesh' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.pial.mesh' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'lh.white.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'lh.white.mesh' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.white.mesh' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'rh.pial.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'rh.pial.mesh' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.pial.mesh' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'rh.white.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'rh.white.mesh' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.white.mesh' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'lh.aparc.a2009s.annot.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'lh.aparc.a2009s.annot.tex' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 
                            'lh.aparc.a2009s.annot.tex' ) )

  command = 'AimsFileConvert ' + \
            ' -i ' + os.path.join( outputFreesurfer04GiftiAndNifti,
                                   'rh.aparc.a2009s.annot.gii' ) + ' ' + \
            ' -o ' + os.path.join( outputFreesurfer05ToNativeSpace,
                                   'rh.aparc.a2009s.annot.tex' )
  print( command )
  os.system( command )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 
                            'rh.aparc.a2009s.annot.tex' ) )

  gkg.executeCommand(
      { 'algorithm' : 'GetTransform3dFromVolumeHeader',
      'parameters' :
          { 'fileNameIn' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                              'aseg.ima' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'transformation.trm' ) ),
            'verbose' : verbose
          },
      'verbose' : verbose
      } )

  gkg.executeCommand(
      { 'algorithm' : 'MeshMapTransform3d',
      'parameters' :
          { 'fileNameMeshMap' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'lh.pial.mesh' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.pial.mesh' ) ),
            'fileNameTransform3ds' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'transformation1.trm' ) ),
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.pial.mesh' ) )

  gkg.executeCommand(
      { 'algorithm' : 'MeshMapTransform3d',
      'parameters' :
          { 'fileNameMeshMap' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'lh.white.mesh' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'lh.white.mesh' ) ),
            'fileNameTransform3ds' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'transformation1.trm' ) ),
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'lh.white.mesh' ) )

  gkg.executeCommand(
      { 'algorithm' : 'MeshMapTransform3d',
      'parameters' :
          { 'fileNameMeshMap' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'rh.pial.mesh' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.pial.mesh' ) ),
            'fileNameTransform3ds' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'transformation1.trm' ) ),
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.pial.mesh' ) )

  gkg.executeCommand(
      { 'algorithm' : 'MeshMapTransform3d',
      'parameters' :
          { 'fileNameMeshMap' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'rh.white.mesh' ) ),
            'fileNameOut' : str( os.path.join( outputFreesurfer05ToNativeSpace,
                                               'rh.white.mesh' ) ),
            'fileNameTransform3ds' : str( os.path.join( 
                                                outputFreesurfer05ToNativeSpace,
                                                'transformation1.trm' ) ),
            'verbose' : verbose
          },
      'verbose' : verbose
      } )
  removeMinf( os.path.join( outputFreesurfer05ToNativeSpace, 'rh.white.mesh' ) )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
