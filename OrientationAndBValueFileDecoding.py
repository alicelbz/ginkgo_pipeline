import os, json, sys, shutil
sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )
import gkg

from CopyFileDirectoryRm import *


def flipping( flippingTypes, orientation ):

  oldOrientation = orientation
  newOrientation = orientation
  for flipping in flippingTypes:
  
    if ( flipping == 'yz' ):
    
      newOrientation[ 0 ] = oldOrientation[ 0 ]
      newOrientation[ 1 ] = oldOrientation[ 2 ]
      newOrientation[ 2 ] = oldOrientation[ 1 ]


    elif ( flipping == 'xy' ):
    
      newOrientation[ 0 ] = oldOrientation[ 1 ]
      newOrientation[ 1 ] = oldOrientation[ 0 ]
      newOrientation[ 2 ] = oldOrientation[ 2 ]

    elif ( flipping == 'xz' ):
    
      newOrientation[ 0 ] = oldOrientation[ 2 ]
      newOrientation[ 1 ] = oldOrientation[ 1 ]
      newOrientation[ 2 ] = oldOrientation[ 0 ]

    elif ( flipping == 'x' ):
    
      newOrientation[ 0 ] = -oldOrientation[ 0 ]
      newOrientation[ 1 ] = oldOrientation[ 1 ]
      newOrientation[ 2 ] = oldOrientation[ 2 ]

    elif ( flipping == 'y' ):
    
      newOrientation[ 0 ] = oldOrientation[ 0 ]
      newOrientation[ 1 ] = -oldOrientation[ 1 ]
      newOrientation[ 2 ] = oldOrientation[ 2 ]

    elif ( flipping == 'z' ):
    
      newOrientation[ 0 ] = oldOrientation[ 0 ]
      newOrientation[ 1 ] = oldOrientation[ 1 ]
      newOrientation[ 2 ] = -oldOrientation[ 2 ]
      
    oldOrientation = newOrientation
    
  return newOrientation


def runOrientationAndBValueFileDecoding( subjectDirectoryGisConversion,
                                         subjectDirectoryTopUpCorrection,
                                         flippingTypes,
                                         description,
                                         outputDirectory,
                                         verbose ):
                      
  
  if ( verbose == True ):
  
    print( "ORIENTATION AND B-VALUE FILE DECODING" )
    print( "-------------------------------------------------------------" )


  # preparing T2, DW index strings as well as orientation & bvalue lists
  listOfFileNameT2s = list()
  listOfFileNameDWs = list()
  fileNameT2s = ()
  fileNameDWIs = ()
  globalDwOrientations = list()
  globalDwBValues = list()
  globalReceiverGains = list()
 
  fileNameDWs = ()
  fileNameBvals = ()
  fileNameBvecs = ()

  for key in sorted( description.keys() ):

    if ( key.startswith( 'dw-' ) and ( not key.startswith( 'dw-b2500-06dir' ) ) ):

      fileNameDwi = os.path.join( subjectDirectoryTopUpCorrection, 
                                  key[:-5] + '.ima' )
      fileNameBval = os.path.join( subjectDirectoryGisConversion, 
                                   key + '.bval' )
      fileNameBvec = os.path.join( subjectDirectoryGisConversion, 
                                   key + '.bvec' )

      fileNameDWs += ( str( fileNameDwi ), )
      fileNameBvals += ( str( fileNameBval ), )
      fileNameBvecs += ( str( fileNameBvec ), )

  if ( verbose == True ):
  
    print( "fileNameDWs : " + str( fileNameDWs ) )

  dwiCount = len( fileNameDWs )
  maximumBValue = 0

  for index in range( 0, dwiCount ):

    # filename extension
    extension = str( index + 1 )

    # preparing T2, DW index strings as well as orientation & bvalue lists
    t2Indices = ''
    dwIndices = ''
    dwBValues = list()
    dwOrientations = list()
    currentDwBValues = list()
    currentDwOrientations = list()

    f = open( fileNameBvals[ index ], 'r' )
    bValLines = f.readlines()
    f.close()

    f = open( fileNameBvecs[ index ], 'r' )
    bVecLines = f.readlines()
    f.close()

    xCoordinates = bVecLines[ 0 ][ : -1 ].split()
    yCoordinates = bVecLines[ 1 ][ : -1 ].split()
    zCoordinates = bVecLines[ 2 ][ : -1 ].split()
    bValues = bValLines[ 0 ][ : -1 ].split()

    count = len( xCoordinates )
    if ( len( bValues ) != count ):
    
      raise( RuntimeError, 'incoherent b-value and orientation files' )

    currentDwBValues = []
    currentDwOrientations = []

    for i in range( 0, count ):
    
      currentDwOrientations.append( [ float( xCoordinates[ i ] ),
                                      float( yCoordinates[ i ] ),
                                      float( zCoordinates[ i ] ) ] )
      currentDwBValues.append( float( bValues[ i ] ) )

    # sanity check
    if ( len( currentDwBValues ) != len( currentDwOrientations ) ):
    
      message = 'b-value and orientation list do not have the same length'
      raise( RuntimeError, message )

    # determining T2 and DW indices
    for dwIndex in range( 0, len( currentDwBValues ) ):

      bValue = currentDwBValues[ dwIndex ]
      orientation = currentDwOrientations[ dwIndex ]
      orientationSquareNorm = orientation[ 0 ] * orientation[ 0 ] + \
                              orientation[ 1 ] * orientation[ 1 ] + \
                              orientation[ 2 ] * orientation[ 2 ]

      if ( ( bValue < 10 ) or
           ( orientationSquareNorm < 1e-3 ) ):

        t2Indices += str( dwIndex ) + ' '
            
      else:
          
        dwIndices += str( dwIndex ) + ' '
        dwBValues.append( bValue )
        dwOrientations.append( orientation )

    if ( verbose == True ):
    
      print( "T2 indices : " + str( t2Indices ) )
      print( "DW indices : " + str( dwIndices ) )
      print( "DW b-values : " + str( dwBValues ) )
      print( "DW orientations : " + str( dwOrientations ) )

    # extracting current T2 multiple volume
    t2FileName = os.path.join( outputDirectory, 't2_' + extension + '.ima' )

    print( 'extracting T2 volume ', extension, ' : \'', t2FileName, '\'' )

    command = 'GkgExecuteCommand SubVolume' + \
              ' -i ' + fileNameDWs[ index ] + \
              ' -o ' + str( t2FileName ) + \
              ' -tIndices ' + str( t2Indices ) + \
              ' -verbose true'
    os.system( command )
    removeMinf( t2FileName )

    # extracting current DW volume
    dwFileName = os.path.join( outputDirectory, 'dw_' + extension + '.ima' )

    print( 'extracting DW volume ', extension, ' : \'', dwFileName, '\'' )

    command = 'GkgExecuteCommand SubVolume' + \
              ' -i ' + fileNameDWs[ index ] + \
              ' -o ' + str( dwFileName ) + \
              ' -tIndices ' + dwIndices + \
              ' -verbose true'
    os.system( command )
    removeMinf( dwFileName )

    # adding current multiple T2, DW volumes, b-values, orientations to 
    # the global list(s)
    listOfFileNameT2s += [ t2FileName ]
    listOfFileNameDWs += [ dwFileName ]
    fileNameT2s += ( str( t2FileName ), )
    fileNameDWIs += ( str( dwFileName ), )
    globalDwOrientations += dwOrientations 
    globalDwBValues += dwBValues
    
    for b in dwBValues:
  
      if ( b > maximumBValue ):
    
        maximumBValue = b

  if ( verbose == True ):
    
    print( 'fileNameT2s : ', fileNameT2s )

  # merging T2 volume(s) together
  fileNameT2Multiple = os.path.join( outputDirectory, 't2_multiple.ima' )
  gkg.executeCommand(
  { 'algorithm' : 'Cat',
    'parameters' : \
      { 'inputNames' : fileNameT2s,
        'outputName' : str( fileNameT2Multiple ),
        'type' : 't',
        'ascii' : False,
        'format' : 'gis',
        'verbose' : True
      },
    'verbose' : True
  } )
  removeMinf( fileNameT2Multiple )

  # averaging T2 volume(s)
  fileNameAverageT2 = os.path.join( outputDirectory, 't2.ima' )

  gkg.executeCommand(
    { 'algorithm' : 'VolumeAverager',
      'parameters' : \
        { 'fileNameIn' : str( fileNameT2Multiple ),
          'fileNameOut' : str( fileNameAverageT2 ),
          'axis' : 't',
          'ascii' : False,
          'format' : 'gis',
          'verbose' : True
        },
      'verbose' : True
    } )
  removeMinf( fileNameAverageT2 )

  # concatenating DW volume(s)
  fileNameDW = os.path.join( outputDirectory, 'dw.ima' )
  gkg.executeCommand(
  { 'algorithm' : 'Cat',
    'parameters' : \
      { 'inputNames' : fileNameDWIs,
        'outputName' : str( fileNameDW ),
        'type' : 't',
        'ascii' : False,
        'format' : 'gis',
        'verbose' : True
      },
    'verbose' : True
  } )
  removeMinf( fileNameDW )

  # saving output global b-value file 
  print( 'global b-value set : ', str( globalDwBValues ) )

  outputBValueFileName = os.path.join( outputDirectory, 'bvalues.txt' )
  f = open( outputBValueFileName, 'w' )
  globalDwBValueCount = len( globalDwBValues )
  f.write( str( globalDwBValueCount ) + '\n' )

  for b in globalDwBValues:
        
    f.write( str( b ) + '\n' )

  f.close()

  # saving output global orientation file    
  print( 'global orientation set : ', str( globalDwOrientations ) )

  outputOrientationFileName = os.path.join( outputDirectory, 'bvec.txt' )
  f = open( outputOrientationFileName, 'w' )
  globalDwOrientationCount = len( globalDwOrientations )
  f.write( str( globalDwOrientationCount ) + '\n' )
  
  for orientation in globalDwOrientations:

    flippedOrientation = flipping( flippingTypes, orientation )      
    f.write( str( flippedOrientation[ 0 ] ) + ' ' + \
             str( flippedOrientation[ 1 ] ) + ' ' + \
             str( flippedOrientation[ 2 ] ) + '\n' )

  f.close()

  
  if ( verbose == True ):

    print( "-------------------------------------------------------------" )
