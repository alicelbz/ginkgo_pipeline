import sys, os, string, inspect, types, glob, fnmatch, re, copy, shutil
import signal, time, errno, socket, platform, tempfile, traceback, stat
import distutils.spawn, operator, tarfile, json

#-----------------------------------------------------------------------------
# copyFile()
#-----------------------------------------------------------------------------

def copyFile( source, dest,
              symlinks=False, 
              copyAsSymlinks=False ):
  '''
  Remove C{dest} file or symbolic link and copy C{source} file to C{dest}. If 
  C{dest} is an existing directory, an C{OSError} exception is raised (this is 
  to avoid removing directories and their content by mistake).
  @param symlinks: if C{True} (default=C{False}), all symbolic links in 
    C{sourceDir} are copied as is in C{C{destinationDir}. For instance, if a 
    symbolic link points to C{a/b/c}, its copy will also point to C{a/b/c}.
  @type  symlinks: bool
  @param copyAsSymlinks: if True (default=C{False}), regular files are not 
    copied but symbolic links are created to these files. Symbolic links in 
    ${sourceDir} are treated as if C{symlinks=True}.
  @type  copyAsSymlinks: bool
  '''
  if not os.path.exists( source ):
    print( source, 'does not exist' )
    return
  if os.path.islink( dest ):
    os.remove( dest )
  elif os.path.exists( dest ):
    os.chmod( dest, stat.S_IWRITE | stat.S_IREAD )
    os.remove( dest )
  else:
    destDir = os.path.dirname( dest )
    if not os.path.isdir( destDir ):
      os.makedirs( destDir )

  if symlinks or copyAsSymlinks:
    if os.path.islink( source ) and not os.path.isabs( os.readlink( source ) ):
      os.symlink( os.readlink( source ), dest )
    elif copyAsSymlinks and systemname != 'windows':
      os.symlink( source, dest )
    else:
      shutil.copy2( source, dest )
  else:
    shutil.copy2( source, dest )


#-----------------------------------------------------------------------------
# copyDirectory()
#-----------------------------------------------------------------------------

def copyDirectory( sourceDir, destinationDir, 
                   symlinks = False, 
                   copyAsSymlinks = False,
                   include = None,
                   exclude = None,
                   copyCallback = None,
                   keepExistingDirs = True ):
  '''
  Copy recursively the content of C{sourceDir} directory in C{destinationDir}   
  directory. All subdirectories directories are created if necessary (including 
  C{destinationDir}).

  @param symlinks: if C{True} (default=C{False}), all symbolic links in 
    C{sourceDir} are copied as is in C{C{destinationDir}. For instance, if a 
    symbolic link points to C{a/b/c}, its copy will also point to C{a/b/c}.
  @type  symlinks: bool

  @param copyAsSymlinks: if True (default=C{False}), regular files are not 
    copied but symbolic links are created to these files. Symbolic links in 
    ${sourceDir} are treated as if C{symlinks=True}.
  @type  copyAsSymlinks: bool

  @param include: Selection of files to copy. If not C{None} (which is the 
    default), files are not copied if C{include.match( fileName )} is false 
    (where C{fileName} is the source file name relative to C{sourceDir}). 
    C{include} has no effect on directories parsing.

  @param exclude: Selection of file or directories to ignore. If not C{None} 
   (which is the default), files are not copied if C{exclude.match( fileName )} 
   is true (where C{fileName} is the source file name relative to 
   C{sourceDir}). C{include} has no effect on directories parsing.

  @param copyCallback: function that is called before the copy of each file 
    (after filtering with C{include} and C{exclude}). If the function return 
    C{False} the file is not copied, otherwise L{copyFile} is called to do the 
    copy. The function is called with two parameters: the source file name and 
    the destination file name.

  @param keepExistingDirs: if True (default=C{True}), already existing
    subdirectories will not be removed or cleaned. This allows mixing several
    source directories in the same destination.

  @see: L{copyFile}
  '''
  #print 'copyDirectory', sourceDir, destinationDir, ', symlinks:', symlinks, \
    #'copyAsSymlinks:', copyAsSymlinks, 'include:', include, \
    #'exclude:', exclude, 'copyCallback:', copyCallback
  if not os.path.exists( sourceDir ):
    return
  stack = os.listdir( sourceDir )
  while stack:
    relSource = stack.pop()
    source = os.path.join( sourceDir, relSource )
    dest = os.path.join( destinationDir, relSource )
    if os.path.islink( source ) or not os.path.isdir( source ):
      if ( include is not None and not include.match( relSource ) ) or \
         ( exclude is not None and exclude.match( relSource ) ):
        continue
      if copyCallback is None or copyCallback( source, dest ):
        copyFile( source, dest, symlinks=symlinks,
                  copyAsSymlinks=copyAsSymlinks )
    elif os.path.isdir( source ):
      if os.path.islink( dest ):
        os.unlink( dest )
      elif os.path.exists( dest ):
        if not keepExistingDirs:
          rm( dest )
      else:
        os.makedirs( dest )
      stack += [os.path.join( relSource, f ) for f in os.listdir( source )]
    else:
      stack += [os.path.join( relSource, f ) for f in os.listdir( source )]


#-----------------------------------------------------------------------------
# rm()
#-----------------------------------------------------------------------------

def rm( *args ):

  sources = []
  for pattern in args:
    sources += glob.glob( pattern )
  sys.stdout.flush()
  for path in sources:
    if not os.path.islink( path ):
      # this test avoids an error on dead symlinks
      os.chmod( path, 0o777 )
    if os.path.isdir( path ) and not os.path.islink( path ):
      rm( os.path.join( path, '*' ) )
      os.rmdir( path )
    else:
      os.remove( path )


#-----------------------------------------------------------------------------
# removeMinf()
#-----------------------------------------------------------------------------

def removeMinf( fileName ):

  fileNameMinf = fileName + '.minf'
  if ( os.path.exists( fileNameMinf ) ):
  
    os.remove( fileNameMinf )


#-----------------------------------------------------------------------------
# makeDirectory()
#-----------------------------------------------------------------------------

def makeDirectory( baseDirectory, directory ):

  outputDirectory = os.path.join( baseDirectory, directory )
  if ( not os.path.exists( outputDirectory ) ):
  
    os.mkdir( outputDirectory )
    
  return outputDirectory
