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

from sys import argv
import time, datetime
import os, glob
import numpy as np

# python script imports
from src import ezplot
from src import ezutils
from src import ezstat

ver = '3.0'
dbg = '<=== debug string ===>'

# main function -- function calls are done here
def main(args):
    # update global arguments
	globals().update(args.__dict__)

	start_time = time.time()

	print("Starting EZlogparse...")
	print("==================================================")

	# check if user wants to analyze a whole directory
	# dir == None == unspecified, therefore ezlogparse
	# will execute with the default single log file in
	# the current working directory of the script
	flag = 0
	if (dir == None):
		data = execute_main(args, infile, outfile, keyword, flag)
	else:
		for filename in sorted(glob.glob(os.path.join(dir,ext))):	
			infile = filename
			data = execute_main(args, infile, outfile, keyword, flag)
			data.global_log_names.append(infile)			
			flag += 1

	print('Overall EZProxy Log Analysis'.format())
	print('Total Connections: {0}'.format(sum(data.global_log_unique_cnt)))
	print('Total On Campus connections: {0}'.format(sum(data.global_on_campus)))
	print('Total Off Campus connections: {0}'.format(sum(data.global_off_campus)))
	print('Total Online Libraries Accessed: {0}'.format(sum(data.global_sites)))
	print("==================================================")
	print('Data file: {0}'.format(outfile))
	print('Stat file: {0}'.format(statfile))
	print('Total run time: {0}'.format(elapsed_time(time.time() - start_time)))
	print("==================================================")

	print(data.global_log_names[0])
	print(data.global_log_unique_cnt)

	# generate plots for statistical data
	# parameters: generate_bar_graph
	# (x_axis, item_label, x_items, y_items, x_label, y_label, title, filename)
	# paramters: generate_pie_chart
	# (sizes, labels, title, filename)
	if (plot and dir!=None):
		ezplot.generate_bar_graph(np.arange(len(data.global_log_names)),
			[s.strip(dir+'ezp.') for s in data.global_log_names],
			data.global_log_names, data.global_log_unique_cnt, '',
			'Total no. of Requests', 'Total no. of Unique Requests in One Year',
			'plot_requests_total.png')
		ezplot.generate_pie_chart([sum(data.global_on_campus), sum(data.global_off_campus)],
			['On Campus', 'Off Campus'], 'Percentage of Total Connections',
			'plot_connections_total.png')
	else: pass

# main subfunction to execute in-case user defines execution
# to run analysis on multiple files in a specified directory
def execute_main(args, infile, outfile, keyword, flag):
	print('Parsing {0}: Keyword "{1}"'.format(infile, keyword))
	print('--------------------------------------------------')
	data = ezutils.parse(infile, args)
	data.filter(keyword)
	data.dt_to_unix_timestamp()
	if (flag == 0): mode = 'w'
	else: mode = 'a'

	print('Parsing done!')
	print('--------------------------------------------------')
	ezstat.generate(args, data, flag)
	csv_string = final_string(data.content)

	# FIXME: for debugging purpose, store original filtered items in a debug file
	# csv_string = final_string(data.filtered_items)
	dump_string_to_out(csv_string, outfile, mode)
	print('--------------------------------------------------')
	print('Statistical Report done!')

	if (dir == None): pass
	else: print('==================================================')
	return data

def elapsed_time(sec):
    # this function returns string converted
    # from the time elapsed, units are adjusted
    # for more readable output
    if sec < 1: return str(sec*1000) + ' msecs'
    elif sec < 60: return str(sec) + ' secs'
    elif sec < (60*60): return str(sec/60) + ' mins'
    else: return str(sec/(60*60)) + ' hrs'

def final_string(strings):
	return '\n'.join(','.join(i) for i in strings) + '\n'

def dump_string_to_out(strings, filename, mode):
	with open(filename, mode) as f: f.write(strings)