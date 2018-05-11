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
import re, argparse
import os, glob

ver = '3.0'
dbg = '<=== debug string ===>'

def main(in_file, out_file, stat_file, keyword, timewindow):
	start_time = time.time()
	print("Starting EZlogparse...")
	print("==================================================")
	# check if user wants to analyze a whole directory
	# dir == None == unspecified, therefore ezlogparse
	# will execute with the default single log file in
	# the current working directory of the script
	flag = 0
	if (dir == None): execute_main(in_file, flag)
	else:
		for filename in glob.glob(os.path.join(dir,ext)):
			in_file = filename
			execute_main(in_file, flag)
			flag += 1
	print('Total run time: {0}'.format(elapsed_time(time.time() - start_time)))

def execute_main(in_file, flag):
	print('Parsing {0}: Keyword "{1}"'.format(in_file, keyword))
	data = parse_ezlog(in_file)
	data.search(keyword)
	data.dt_to_unix_timestamp()
	mode = ''
	if (flag == 0): mode = 'w'
	else: mode = 'a'

	print('Parsing done!')
	print('Data file: {0}'.format(out_file))
	print('--------------------------------------------------')
	generate_statistics(data, timewindow, flag)
	csv_string = '\n'.join(i for i in data.string)
	dump_string_to_out(csv_string, out_file, mode)
	print('--------------------------------------------------')
	print('Statistical Report done!')
	print('Stat file: {0}'.format(stat_file))

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
	def __init__(self, in_file):

		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]
		#used in search function
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
		self.basetime = 0

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
		temp = zip(self.ip[a:b+1], self.request[a:b+1])
		unique = set()
		for i, element in enumerate(temp):
			if element not in unique:
				self.indices.append(a + i)
			unique.add(element)
		duplicates = list(zip(*unique))

		if len(duplicates) > 0:
			duplicates = duplicates.pop(1)
			duplicates = Counter(duplicates)

			for i, j in enumerate(duplicates.most_common(), 1):
				self.string.append('CID: {0:03d}, No. of requests: {1}'.format(i, j[1]))
				if (verbose): print(self.string[-1])
			self.string.append('Number of Unique URLs: {}'.format(len(set(duplicates))))
			if (verbose): print(self.string[-1])

		for i, j in enumerate(unique, 1):
			self.string.append('IP{}: {}\nURL{}: {}'.format(i, j[0], i, j[1]))

		self.string.append('Number of Unique IP: {}'.format(i))
		if (verbose): print(self.string[-1])

	def final_content(self):
		temp = list(zip(self.ip, self.name, self.date, self.tzone,
			list(map(str, self.unixtime)), self.request, self.bytes))
		for i in self.indices:
			self.content.append(temp[i])

def count_oncampus_occurences(data_in, strings):
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
	strings.append('Number of off-campus accesses: {0}'.format(off_campus_count+1))
	if (verbose): print(strings[-1])

def dump_string_to_out(strings, filename, mode):
	with open(filename, mode) as f: f.write(strings)

def generate_statistics(items, timewindow, flag):
	mode = ''
	finaltime = items.unixtime[len(items.unixtime)-1]
	elapsedtime = finaltime - items.unixtime[0]
	timeslices = int((elapsedtime/timewindow)+1)

	print('Generating Statistics')
	print('Initial timestamp: {0} [{1}]'.format(items.unixtime[0], 0))
	print('Final timestamp: {0} [{1}]'.format(
		items.unixtime[len(items.unixtime)-1], len(items.unixtime)-1))
	print('Total number of items: {0}'.format(len(items.unixtime)))
	print('Number of time slices: {0}'.format(timeslices))
	print('Per time slice: {0} seconds.'.format(timewindow))

	if (flag == 0): mode = 'w'
	else: mode = 'a'
	iter = 1
	for x in range(timeslices):
		if (verbose): print('--------------------------------------------------')

		# set initial value of lowerbound index to 0 in the first iteration
		if items.basetime is 0:
			items.basetime = items.unixtime[0]
		items.string.append('Timeslice no. {0} ({1} - {2})'.format(
			iter, items.basetime, items.basetime+timewindow))
		if (verbose): print(items.string[-1])

		# initialize time slice indices
		uppertime = items.basetime + timewindow
		baseindex = items.locate_index(items.basetime)

		# set ceiling value for uppertime
		if uppertime >= items.unixtime[-1]: uppertime = items.unixtime[-1]
		upperindex = items.locate_index(uppertime)

		#print(upperindex)
		if upperindex != baseindex:
			if (x != timeslices-1): upperindex -= 1
			else: upperindex = items.locate_index(uppertime)

		# get unixtime value of upperbound and lowerbound indices
		baseindexvalue = items.unixtime[baseindex]
		upperindexvalue = items.unixtime[upperindex]
		#print(upperindex)

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
		items.string.append('Number of items in sublist: {0}'.format(
			len(items.unixtime[baseindex:upperindex])+1))
		if (verbose): print(items.string[-1])
		# statistical function generation starts here
		count_oncampus_occurences(items.filtered_items[baseindex:upperindex], items.string)
		items.unique_content(baseindex, upperindex)
		# checks if timeslice is the last one
		# ends loop if timeslice reaches EOL
		if x == timeslices-1: break
		else: items.basetime = uppertime
		iter += 1
	items.final_content()
	temp = '\n'.join(i for i in items.string)
	dump_string_to_out(temp, stat_file, mode)

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
		'--out_file','-o',type = str,
		help = 'Use custom output file',default = 'parsed.csv'
	)
	parser.add_argument(
		'--stat_file','-s',type = str,
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
			out_file = args.out_file,
			stat_file = args.stat_file,
			keyword = args.keyword,
			timewindow = args.timewindow
)
