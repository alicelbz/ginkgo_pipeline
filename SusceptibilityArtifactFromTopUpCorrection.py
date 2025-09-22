import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
from core.command.CommandFactory import *

from CopyFileDirectoryRm import *

def getSize( fileNameIma ):

  f = open( fileNameIma[ : -3 ] + 'dim', 'r' )
  lines = f.readlines()
  f.close()
  line1 = lines[ 0 ].split()
  sizeX = int( line1[ 0 ] )
  sizeY = int( line1[ 1 ] )
  sizeZ = int( line1[ 2 ] )
  sizeT = int( line1[ 3 ] )

  return [ sizeX, sizeY, sizeZ, sizeT ]

def runTopUpCorrection( subjectDirectoryNiftiConversion,
                        description,
                        differentTopUpAcquisitions,
                        timePoint,
                        outputDirectory,
                        verbose ):
                      
  
  if ( verbose == True ):
  
    print( "SUSCEPTIBILITY ARTIFACT CORRECTION FROM TOP UP" )
    print( "-------------------------------------------------------------" )

  # computing transformation from blip-up & blip-down references
  fileNameB0TopUpReferences = os.path.join( outputDirectory,
                                            'topup_references' )
         
  fileNameB01Up = os.path.join( subjectDirectoryNiftiConversion, 
                                'b0-b2500-06dir-PEP1.nii.gz' )
 # fileNameB01Dn = os.path.join( subjectDirectoryNiftiConversion, 
 #                               'b0-b2500-60dir-PEP0.nii.gz' )
  fileNameB02Dn = os.path.join( subjectDirectoryNiftiConversion, 
                                'b0-b1500-45dir-PEP0.nii.gz' )
 # fileNameB03Dn = os.path.join( subjectDirectoryNiftiConversion, 
 #                               'b0-b0200-30dir-PEP0.nii.gz' )

  if timePoint in differentTopUpAcquisitions:

    if "TopUpReferenceDn" in differentTopUpAcquisitions[ timePoint ]:

      fileNameB02Dn = os.path.join( subjectDirectoryNiftiConversion, 
                                    differentTopUpAcquisitions[ timePoint ][ "TopUpReferenceDn" ] )
      
    if "TopUpReferenceUp" in differentTopUpAcquisitions[ timePoint ]:

      fileNameB01Up = os.path.join( subjectDirectoryNiftiConversion, 
                                    differentTopUpAcquisitions[ timePoint ][ "TopUpReferenceUp" ] )

                                   

  # command = 'fslmerge ' + \
  #            ' -t ' + fileNameB0TopUpReferences + ' ' + \
  #            fileNameB01Up + ' ' + \
  #            fileNameB01Dn + ' ' + \
  #            fileNameB02Dn + ' ' + \
  #            fileNameB03Dn
  command = 'fslmerge ' + \
             ' -t ' + fileNameB0TopUpReferences + ' ' + \
             fileNameB01Up + ' ' + \
             fileNameB02Dn
  print( command )
  os.system( command )

  # creating the acquisition parameters text file
  fileNameTopUpParameters = os.path.join( outputDirectory,
                                          'top_up_acquisition_parameters.txt' )
  # file = open( fileNameTopUpParameters, 'w' )
  # file.write( '0 1 0 0.052\n' )
  # file.write( '0 -1 0 0.052\n' )
  # file.write( '0 -1 0 0.052\n' )
  # file.write( '0 -1 0 0.052' )
  # file.close()

  file = open( fileNameTopUpParameters, 'w' )
  file.write( '0 1 0 0.052\n' )
  file.write( '0 -1 0 0.052' )
  file.close()

  ###
  # echo spacing : 0.325
  # epi factor : 160
  # 0.052 = 0.001*0.325*160
  ###

  # computing top-up transformation
  fileNameTopUpTransformation = os.path.join( outputDirectory,
                                              'top_up_transformation' )
  command = 'topup ' + \
            ' --imain=' + fileNameB0TopUpReferences + ' ' + \
            ' --datain=' + fileNameTopUpParameters + ' ' + \
            ' --config=b02b0.cnf' + ' ' + \
            ' --out=' + fileNameTopUpTransformation + ' ' +  \
            ' -v'
  print( command )
  os.system( command )

  # applying top-up to NIFTI DWI
  for key in sorted( description.keys() ):

    if ( key.startswith( "dw" ) ) and ( key.endswith( "PEP0" ) ):
  
      fileNameDwi = os.path.join( subjectDirectoryNiftiConversion,
                                  key + '.nii.gz' )
      fileNameOut = os.path.join( outputDirectory, key[:-5] + '.nii.gz' )
      command = 'applytopup ' + \
                ' --imain=' + fileNameDwi + \
                ' --datain=' + fileNameTopUpParameters + \
                ' --inindex=2 ' + \
                ' --topup=' + fileNameTopUpTransformation + \
                ' --method=jac ' + \
                ' --interp=spline ' + \
                ' --out=' + fileNameOut + \
                ' --verbose'
      print( command )
      os.system( command )

      fileNameOutGis = os.path.join( outputDirectory, key[:-5] + '.ima' )

      CommandFactory().executeCommand(
        { 'algorithm' : 'Nifti2GisConverter',
          'parameters' : \
          { 'fileNameIn' : str( fileNameOut ),
            'fileNameOut' : str( fileNameOutGis ),
            'outputFormat' : 'gis',
            'ascii' : False,
            'verbose' : verbose
          },
          'verbose' : verbose
        } )
      removeMinf( fileNameOutGis )

    elif ( key.startswith( "dw" ) ) and ( key.endswith( "PEP1" ) ):
  
      fileNameDwi = os.path.join( subjectDirectoryNiftiConversion,
                                  key + '.nii.gz' )
      fileNameOut = os.path.join( outputDirectory, key[:-5] + '.nii.gz' )
      command = 'applytopup ' + \
                ' --imain=' + fileNameDwi + \
                ' --datain=' + fileNameTopUpParameters + \
                ' --inindex=1 ' + \
                ' --topup=' + fileNameTopUpTransformation + \
                ' --method=jac ' + \
                ' --interp=spline ' + \
                ' --out=' + fileNameOut + \
                ' --verbose'
      print( command )
      os.system( command )

      fileNameOutGis = os.path.join( outputDirectory, key[:-5] + '.ima' )

      CommandFactory().executeCommand(
        { 'algorithm' : 'Nifti2GisConverter',
          'parameters' : \
          { 'fileNameIn' : str( fileNameOut ),
            'fileNameOut' : str( fileNameOutGis ),
            'outputFormat' : 'gis',
            'ascii' : False,
            'verbose' : verbose
          },
          'verbose' : verbose
        } )
      removeMinf( fileNameOutGis )

  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
