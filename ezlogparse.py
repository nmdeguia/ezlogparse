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
import ipaddress
import time, datetime
import argparse
import os, glob
import numpy as np

# python script imports
from src import ezplot
from src import ezparse

ver = '3.0'
dbg = '<=== debug string ===>'

# global variable declarations
global_log_unique_cnt = []
global_log_names = []
global_on_campus = []
global_off_campus = []

# main function -- function calls are done here
def main(in_file, outfile, statfile, keyword, timewindow):
	start_time = time.time()

	print("Starting EZlogparse...")
	print("==================================================")

	# check if user wants to analyze a whole directory
	# dir == None == unspecified, therefore ezlogparse
	# will execute with the default single log file in
	# the current working directory of the script
	flag = 0
	if (dir == None):
		execute_main(in_file, flag)
	else:
		for filename in sorted(glob.glob(os.path.join(dir,ext))):
			in_file = filename
			global_log_names.append(in_file)
			execute_main(in_file, flag)
			flag += 1

	print('Overall EZProxy Log Analysis'.format())
	print('Total Connections: {0}'.format(sum(global_log_unique_cnt)))
	print('Total On Campus connections: {0}'.format(sum(global_on_campus)))
	print('Total Off Campus connections: {0}'.format(sum(global_off_campus)))
	print("==================================================")
	print('Data file: {0}'.format(outfile))
	print('Stat file: {0}'.format(statfile))
	print('Total run time: {0}'.format(elapsed_time(time.time() - start_time)))
	print("==================================================")	

	# generate plots for statistical data
	# parameters: generate_bar_graph
	# (x_axis, item_label, x_items, y_items, x_label, y_label, title, filename)
	# paramters: generate_pie_chart
	# (sizes, labels, title, filename)
	if (plot and dir!=None):
		ezplot.generate_bar_graph(np.arange(len(global_log_names)),
			[s.strip(dir+'ezp.') for s in global_log_names], global_log_names,
			global_log_unique_cnt, '', 'Total no. of Requests',
			'Total no. of Unique Requests in One Year',
			'plot_requests_total.png')
		ezplot.generate_pie_chart([sum(global_on_campus), sum(global_off_campus)],
			['On Campus', 'Off Campus'], 'Percentage of Total Connections',
			'plot_connections_total')
	else: pass

# main subfunction to execute in-case user defines execution
# to run analysis on multiple files in a specified directory
def execute_main(in_file, flag):
	print('Parsing {0}: Keyword "{1}"'.format(in_file, keyword))
	print('--------------------------------------------------')
	data = ezparse.parse_ezlog(in_file)
	data.search(keyword)
	data.dt_to_unix_timestamp()
	if (flag == 0): mode = 'w'
	else: mode = 'a'

	print('Parsing done!')
	print('--------------------------------------------------')
	generate_statistics(data, timewindow, flag)
	csv_string = final_string(data.content)

	# FIXME: for debugging purpose, store original filtered items in a debug file
	# csv_string = final_string(data.filtered_items)
	dump_string_to_out(csv_string, outfile, mode)
	print('--------------------------------------------------')
	print('Statistical Report done!')

	if (dir == None): pass
	else: print('==================================================')

def elapsed_time(sec):
    # this function returns string converted
    # from the time elapsed, units are adjusted
    # for more readable output
    if sec < 1: return str(sec*1000) + ' msecs'
    elif sec < 60: return str(sec) + ' secs'
    elif sec < (60*60): return str(sec/60) + ' mins'
    else: return str(sec/(60*60)) + ' hrs'

def cnt_oncampus_requests(data_in, strings):
	on_campus_count = 0
	off_campus_count = 0
	unicode_ip_net = str(oncampaddr)
	for i in range(len(data_in)):
		unicode_ip_request = str(data_in[i][0])
		if ipaddress.ip_address(
			unicode_ip_request) in ipaddress.ip_network(unicode_ip_net):
			on_campus_count += 1
		else:
			off_campus_count += 1
	strings.append('Number of on-campus accesses: {0}'.format(on_campus_count))
	if (verbose): print(strings[-1])
	strings.append('Number of off-campus accesses: {0}'.format(off_campus_count))
	if (verbose): print(strings[-1])
	return on_campus_count, off_campus_count

def final_string(strings):
	return '\n'.join(','.join(i) for i in strings) + '\n'

def dump_string_to_out(strings, filename, mode):
	with open(filename, mode) as f: f.write(strings)

def generate_statistics(items, timewindow, flag):
	# set initial value of lowerbound index to 0 in the first iteration    	
	basetime = items.unixtime[0]
	finaltime = items.unixtime[-1]
	elapsedtime = finaltime - items.unixtime[0]
	timeslices = int((elapsedtime/timewindow)+1)

	print('Generating Statistics')
	print('Initial timestamp: {0} [{1}]'.format(items.unixtime[0], 0))
	print('Final timestamp: {0} [{1}]'.format(finaltime, len(items.unixtime)-1))
	print('Per time slice: {0} seconds.'.format(timewindow))
	# print('Total number of items: {0}'.format(len(items.unixtime)))
	print('Number of time slices: {0}'.format(timeslices))

	if (flag == 0): mode = 'w'
	else: mode = 'a'

	for iter, x in enumerate(range(timeslices),1):
		if (verbose): print('--------------------------------------------------')

		# set initial value of lowerbound index to 0 in the first iteration
		# if basetime is 0:
		#	basetime = items.unixtime[0]
		items.string.append('Timeslice no. {0} ({1} - {2})'.format(
			iter, basetime, basetime+timewindow))
		if (verbose): print(items.string[-1])

		# initialize time slice indices
		uppertime = basetime + timewindow
		baseindex = items.locate_index(basetime)

		# set ceiling value for uppertime
		if uppertime >= items.unixtime[-1]: uppertime = items.unixtime[-1]
		upperindex = items.locate_index(uppertime)

		if upperindex != baseindex:
			#length = len(items.unixtime[baseindex:upperindex])
			if (x != timeslices-1): upperindex -= 1
			else: upperindex = items.locate_index(uppertime)
		# else: length = 0

		# get unixtime value of upperbound and lowerbound indices
		baseindexvalue = items.unixtime[baseindex]
		upperindexvalue = items.unixtime[upperindex]

		items.string.append('{0} to {1}'.format(
			datetime.datetime.fromtimestamp(
				int(baseindexvalue)).strftime('%Y-%m-%d %H:%M:%S'),
			datetime.datetime.fromtimestamp(
				int(upperindexvalue)).strftime('%Y-%m-%d %H:%M:%S')
			))
		if (verbose): print(items.string[-1])
		items.string.append('Base: {0} [{1}], Upper: {2} [{3}]'.format(
			baseindexvalue, baseindex, upperindexvalue, upperindex))
		if (verbose): print(items.string[-1])
		# items.string.append('Number of items in sublist: {0}'.format(length))
		# if (verbose): print(items.string[-1])

		# statistical function generation starts here
		unique = items.unique_content(baseindex, upperindex)
		on_conn, off_conn = cnt_oncampus_requests(unique, items.string)

		# get total number of unique items per logfile
		if (iter == 1):
			unique_items = len(unique)
			unique_on_conn = on_conn
			unique_off_conn = off_conn
		else:
			unique_items += len(unique)
			unique_on_conn += on_conn
			unique_off_conn += off_conn

		# checks if timeslice is the last one
		# ends loop if timeslice reaches EOL
		if x == timeslices-1: break
		else: basetime = uppertime

	global_log_unique_cnt.append(unique_items)
	global_on_campus.append(unique_on_conn)
	global_off_campus.append(unique_off_conn)

	items.string.append('Total no. of unique items in log: {0}'.format(unique_items))
	print (items.string[-1])
	items.final_content()
	temp = '\n'.join(i for i in items.string) + '\n'
	dump_string_to_out(temp, statfile, mode)	    				

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
		'--in_file','-f',type = str,
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
		main(
			in_file = args.in_file,
			outfile = args.outfile,
			statfile = args.statfile,
			keyword = args.keyword,
			timewindow = args.timewindow
			)
		print('Program terminated...'.format())