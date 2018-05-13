# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab
#
# Authors:
#		Bandiola, Al Tristan
#		de Guia, Norman Roy
#
# This script is made specifically for the analysis of ezproxy logs,
# which would later be used for the completion of our capstone project.
#
# Usage: $ python ezlogparse.py --argument value
#
# More details in github.com/nmdeguia/ezlogparse/README.md

import argparse
from src import ezparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--dir','-d',type = str,
        help = 'Directory of logs to parse',default = None
        # directory is the current working directory
        # if this is unspecified, then the parser
        # will only analyze one default/specified log
    )
    group.add_argument(
        '--infile','-f',type = str,
        help = 'Use custom input file',default = 'data.log'
    )
    parser.add_argument(
        '--ext','-e',type = str,
        help = 'File extension of logs',default = '*.log'
        # need to specify * if we want to run the script
        # on all the files with that file extension.
        # Note that if you want to run multiple files,
        # the script only works by opening a separate directory
        # from the current working directory of the script
    )
    parser.add_argument(
        '--outfile','-o',type = str,
        help = 'Use custom output file',default = 'parsed.csv'
    )
    parser.add_argument(
        '--statfile','-s',type = str,
        help = 'Use custom statistics file',default = 'stat.csv'
    )
    parser.add_argument(
        '--keyword','-k',type = str,
        help = 'Specify keyword',default = '.pdf'
    )
    parser.add_argument(
        '--timewindow','-t',type = int,
        help = 'Specify timewindow',default = 14400
    )
    parser.add_argument(
        '--oncampaddr','-ipc',type = str,
        help = 'Specify campus ip address',default = '10.0.0.0/8'
    )
    parser.add_argument(
        # plot only works for multiple files for now
        # specifically, when you pass the argument --dir
        '--plot','-p',action = 'store_true',
        help = 'Plot statistical graphs'
    )
    parser.add_argument(
        '--verbose','-v',action = 'store_true',
        help = 'Print verbose conversions'
    )
    parser.add_argument(
        '--version',action = 'store_true',
        help = 'Prints version'
    )
    args = parser.parse_args()
    # passes arguments to global namespace:
    globals().update(args.__dict__)
    if (version): print('EZlogparse v{0}'.format(ver))
    else:
        ezparse.main(
            infile = args.infile,
            outfile = args.outfile,
            statfile = args.statfile,
            keyword = args.keyword,
            timewindow = args.timewindow,
            ext = args.ext,
            dir = args.dir,
            oncampaddr = args.oncampaddr,
            plot = args.plot,
            verbose = args.verbose
            )
        print('Program terminated...'.format())
