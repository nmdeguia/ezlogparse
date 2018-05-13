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
from collections import Counter
from bisect import bisect_left
import ipaddress
import time, datetime
import re
import os, glob
import numpy as np

# python script imports
# this imports the plotting functions to generate graphs/plots
# for parsed and analyzed ezproxy log data
from src import ezplot

ver = '3.0'
dbg = '<=== debug string ===>'

# global variable declarations
global_log_unique_cnt = []
global_log_names = []
global_on_campus = []
global_off_campus = []
global_verbose = False

# main function -- function calls are done here
def main(infile, outfile, statfile, keyword, timewindow,
	ext, dir, oncampaddr, plot, verbose):
	start_time = time.time()
	global global_verbose
	global_verbose = verbose

	print("Starting EZlogparse...")
	print("==================================================")

	# check if user wants to analyze a whole directory
	# dir == None == unspecified, therefore ezlogparse
	# will execute with the default single log file in
	# the current working directory of the script
	flag = 0
	if (dir == None):
		execute_main(infile, outfile, keyword, timewindow, oncampaddr, statfile, flag)
	else:
		for filename in sorted(glob.glob(os.path.join(dir,ext))):
			infile = filename
			global_log_names.append(infile)
			execute_main(infile, outfile, keyword, timewindow, oncampaddr, statfile, flag)
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
def execute_main(infile, outfile, keyword, timewindow, oncampaddr, statfile, flag):
	print('Parsing {0}: Keyword "{1}"'.format(infile, keyword))
	print('--------------------------------------------------')
	data = parse_ezlog(infile)
	data.search(keyword)
	data.dt_to_unix_timestamp()
	if (flag == 0): mode = 'w'
	else: mode = 'a'

	print('Parsing done!')
	print('--------------------------------------------------')
	generate_statistics(data, timewindow, oncampaddr, statfile, flag)
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

class parse_ezlog(object):
	def __init__(self, infile):

		with open(infile, 'r') as f:
			self.str_split = [i.split() for i in f]
		# used in search function
		self.filtered_items = list()
		self.content = list()
		self.indices = list()
		self.string = list()

		self.ip = list()			#0
		self.name = list()			#2
		self.date = list()			#3[
		self.tzone = list()			#4]
		self.request = list()		#6
		self.bytes = list()			#7

		self.unixtime = list()

	def search(self, keyword):
		for i in range(len(self.str_split)):
			for j in range(7):	#search all fields
				if keyword in self.str_split[i][j]:
					self.filtered_items.append(self.str_split[i])

		for i in range(len(self.filtered_items)):
			self.ip.append(self.filtered_items[i][0])
			self.name.append(self.filtered_items[i][2])
			self.date.append(self.filtered_items[i][3].strip('['))
			self.tzone.append(self.filtered_items[i][4].strip(']'))
			self.request.append(self.filtered_items[i][6])
			self.bytes.append(self.filtered_items[i][9])

	def dt_to_unix_timestamp(self):
		for i in range(len(self.date)):
			dt = re.split(r'[[/:]+', self.filtered_items[i][3])
			dt[2] = time.strptime(dt[2], '%b').tm_mon # month to number
			dt.pop(0) # remove blank element from start of list
			dt = list(map(int, dt))
			tz = int(self.tzone[i][2:])
			# convert dt to unix timestamp:
			# dt_temp = date.datetime(yr,mo,day,hr,min,sec,tz) = float
			temp = datetime.datetime(dt[2],dt[1],dt[0],dt[3],dt[4],dt[5],tz)
			self.unixtime.append(int(time.mktime(temp.timetuple())))
		return self.unixtime

	# locates the nearest number to the left of timelookup
	def locate_index(self, timelookup):
		index = bisect_left(self.unixtime,timelookup) # returns index
		return int(index)

	def unique_content(self, a, b):
		temp = zip(self.ip[a:b], self.request[a:b])
		unique = set()
		for i, element in enumerate(temp):
			if element not in unique:
				self.indices.append(a + i)
			unique.add(element)
		duplicates = list(zip(*unique))

		if len(duplicates) > 0:
			temp = Counter(duplicates.pop(1))
			for i, j in enumerate(temp.most_common(), 1):
				self.string.append('CID: {0:03d}, No. of requests: {1}'.format(i, j[1]))
				if (global_verbose): print(self.string[-1])
			self.string.append('Number of Unique URLs: {0}'.format(len(set(temp))))
			if (global_verbose): print(self.string[-1])

		for i, j in enumerate(unique, 1):
			self.string.append('IP{0}: {1}\nURL{2}: {3}'.format(i, j[0], i, j[1]))

		self.string.append('Number of Unique IP: {0}'.format(len(list(unique))))
		if (global_verbose): print(self.string[-1])
		return list(unique)

	def unique_sites(self, a, b):
		pass

	def final_content(self):
		temp = list(zip(self.ip, self.name, self.date, self.tzone,
			list(map(str, self.unixtime)), self.request, self.bytes))
		for i in self.indices:
			self.content.append(temp[i])

def cnt_oncampus_requests(data_in, oncampaddr,strings):
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
	if (global_verbose): print(strings[-1])
	strings.append('Number of off-campus accesses: {0}'.format(off_campus_count))
	if (global_verbose): print(strings[-1])
	return on_campus_count, off_campus_count

def final_string(strings):
	return '\n'.join(','.join(i) for i in strings) + '\n'

def dump_string_to_out(strings, filename, mode):
	with open(filename, mode) as f: f.write(strings)

def generate_statistics(items, timewindow, oncampaddr, statfile, flag):
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
		if (global_verbose): print('--------------------------------------------------')

		# set initial value of lowerbound index to 0 in the first iteration
		# if basetime is 0:
		#	basetime = items.unixtime[0]
		items.string.append('Timeslice no. {0} ({1} - {2})'.format(
			iter, basetime, basetime+timewindow))
		if (global_verbose): print(items.string[-1])

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
		if (global_verbose): print(items.string[-1])
		items.string.append('Base: {0} [{1}], Upper: {2} [{3}]'.format(
			baseindexvalue, baseindex, upperindexvalue, upperindex))
		if (global_verbose): print(items.string[-1])
		# items.string.append('Number of items in sublist: {0}'.format(length))
		# if (global_verbose): print(items.string[-1])

		# statistical function generation starts here
		unique = items.unique_content(baseindex, upperindex)
		on_conn, off_conn = cnt_oncampus_requests(unique, oncampaddr, items.string)

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