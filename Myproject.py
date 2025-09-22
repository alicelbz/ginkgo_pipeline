import os
import sys
import optparse



################################################################################
# adding gkg and gkg-private to python path(s)
################################################################################

# gkg ##########################################################################

sys.path.insert( 0, os.path.join( os.sep, 'usr', 'share', 'gkg', 'python' ) )

# gkg-pipeline #################################################################

pyMyprojectPath = os.path.join( '/home/leberre/myproject' )

sys.path.insert( 0, os.path.join( os.sep, 'usr', 'python' ) )
sys.path.insert( 0, pyMyprojectPath )


################################################################################
# parser to get option(s)
################################################################################

parser = optparse.OptionParser()
parser.add_option( '-i', '--inputDicomDirectory',
                   dest = 'inputDicomDirectory',
                   help = 'Myproject input DICOM directory' )
parser.add_option( '-s', '--subjectJsonFileName',
                   dest = 'subjectJsonFileName',
                   help = 'Subject json dictionary filename' )
parser.add_option( '-t', '--taskJsonFileName',
                   dest = 'taskJsonFileName',
                   help = 'Tasks json dictionary filename' )
parser.add_option( '-p', '--timePoint',
                   dest = 'timePoint',
                   default = False,
                   help = 'Myproject timePoint' )
parser.add_option( '-o', '--outputDicomDirectory',
                   dest = 'outputDicomDirectory',
                   help = 'Myproject output DICOM directory' )
parser.add_option( '-v', '--verbose',
                   dest = 'verbose',
                   action = 'store_true',
                   default = False,
                   help = 'Show as much information as possible '
                          '(default: %default)' )

( options, args ) = parser.parse_args()


################################################################################
# 1) Data conversion
################################################################################

from RunPipeline import *

runPipeline( options.inputDicomDirectory,
             options.subjectJsonFileName,
             options.taskJsonFileName,
             options.timePoint,
             options.outputDicomDirectory,
             options.verbose )

