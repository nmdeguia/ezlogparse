# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab #

from sys import argv
from collections import Counter
from bisect import bisect_left
import time
import datetime
import re
import argparse

ezlogparse_version = '2.0'
debug = 'nice, that line is correct'
# just a debug string
# print whenever needed

def main(in_file, out_file, stat_file, keyword, timewindow):
	
	start_time = time.time() 
	print 'EZlogparse v{0}'.format(ezlogparse_version)
	print '--------------------------------------------------'	
	print 'Parsing {0}: Keyword "{1}"'.format(in_file, keyword)

	data = parse_ezlog(in_file)
	data.search(keyword)
	data.extract()
	data.dt_to_unix_timestamp()

	csv_string = dumpstring(data)
	dump_string_to_out(csv_string, out_file)
	print 'Parsing done!'	
	print 'Data file: {0}'.format(out_file)
	print '--------------------------------------------------'

	if (genstat):
		generate_statistics(data, timewindow)
		#dump_string_to_out(data.str_stat, stat_file)
		print '--------------------------------------------------'
		print 'Statistical report complete'
		print 'Stat file: {0}'.format(stat_file)

	total_time = (time.time() - start_time)/100.0
	print 'Total run time: {0}'.format(elapsed_time(time.time() - start_time))

def elapsed_time(sec):
    # this function returns string converted
    # from the time elapsed, units are adjusted
    # for more readable output
    if sec < 1: return str(sec*1000) + ' usecs'
    elif sec < 60: return str(sec) + ' secs'
    elif sec < (60*60): return str(sec/60) + ' mins'
    else: return str(sec/(60*60)) + ' hrs'      
	
class parse_ezlog(object):
	
	def __init__(self, in_file):
		file = open(in_file, 'r')
		raw = list(in_file)
		file.close()

		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]
		
		#used in search function				
		self.filtered_items = list()	
		
		self.ip = list()		#0
		self.name = list()		#2
		self.date = list()		#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		
		self.request_rank = list()
		self.str_stat = ""
		self.str_stat1 = ""
		self.str_stat2 = ""
		self.str_stat3 = ""
		self.unique = list()
		self.unixtime = list()
		self.basetime = 0
		
	def search(self, keyword):
		for i in range(len(self.str_split)):
			for j in range(7):	#search all fields
				if keyword in self.str_split[i][j]:
					self.filtered_items.append(self.str_split[i])
		return self.filtered_items
		
	def extract(self):
		for i in range(len(self.filtered_items)):
			self.ip.append(self.filtered_items[i][0])
			self.name.append(self.filtered_items[i][2])
			self.date.append(self.filtered_items[i][3].strip('['))
			self.tzone.append(self.filtered_items[i][4].strip(']'))
			self.request.append(self.filtered_items[i][6])
			self.bytes.append(self.filtered_items[i][9])
		
	def ranking(self, a, b):
		count = 0
		if (verbose): print 'Count of duplicate URLs:'
		self.request_count = Counter(self.request[a:b+1])
		#self.request_rank = list(self.request_count.most_common())
		for i in self.request_count.most_common():
			count += 1
			string = 'Content ID: {0:03d}, Number of requests: {1}'.format(count, i[1])
			if (verbose): print string
			append_string_to_out(string + '\n', stat_file)
		
	def unique_content(self, a, b):
		count = 0
		#self.unique = Counter(set(zip(self.ip[a:b+1], self.request[a:b+1])))
		self.unique = set(zip(self.ip[a:b+1], self.request[a:b+1]))
		#self.unique = set(self.request[a:b+1])
		#print 'Unique URLs:'
		for i in self.unique:
			count += 1
			string = 'IP{}: {}\nURL{}: {}'.format(count, i[0], count, i[1])
			append_string_to_out(string + '\n', stat_file)
			
		string = 'Number of unique URLs: {}'.format(count)
		if (verbose): print string
		append_string_to_out(string + '\n', stat_file)

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
		#print 'Temp date is = {}'.format(temp)
		#print 'Base time is: {}'.format(self.unixtime[0])
		return self.unixtime

	def locate_index(self, timelookup):	# locates the nearest number to the left of timelookup    	
		index = bisect_left(self.unixtime,timelookup)	# returns index
		return int(index)
		
	def get_slice_timewindow(self, time, timewindow):
		if time is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = time
		print '({} - {})'.format(new_basetime, new_basetime + timewindow)
		return new_basetime

def count_oncampus_occurences(data_in):
	on_campus_count = 0
	off_campus_count = 0   		
	for i in range(len(data_in)):
		if data_in[i][0].startswith(oncampaddr):
			on_campus_count += 1
		else:
			off_campus_count += 1
	string = 'Number of on-campus accesses: {0}\n'.format(on_campus_count)
	string += 'Number of off-campus accesses: {0}'.format(off_campus_count + 1)
	if (verbose): print string
	append_string_to_out(string + '\n', stat_file)

	
def generate_statistics(items, timewindow):
	finaltime = items.unixtime[len(items.unixtime)-1]
	elapsedtime = finaltime - items.unixtime[0]
	timeslices = (elapsedtime/timewindow)+1
	
	print 'Generating Statistics'
	string = 'Initial timestamp: {0} [{1}]'.format(items.unixtime[0], 0) + '\n'
	string += 'Final timestamp: {0} [{1}]'.format(items.unixtime[len(items.unixtime)-1],len(items.unixtime)-1)+'\n'
	string += 'Total number of items: {0}'.format(len(items.unixtime))  + '\n'
	string += 'Number of time slices: {0}.'.format(timeslices) + '\n'
	string += 'Per time slice: {0} seconds.'.format(timewindow)
	
	print string
	dump_string_to_out(string + '\n', stat_file)

	iter = 1
	for x in range(timeslices):
		if (verbose): print '--------------------------------------------------'.format()
		if items.basetime is 0:
			items.basetime = items.unixtime[0]
		string = 'Timeslice no. {0} ({1} - {2})\n'.format(iter, items.basetime, items.basetime + timewindow)
		
		#basetime = items.get_slice_timewindow(items.basetime, timewindow)
		uppertime = items.basetime + timewindow
		baseindex = items.locate_index(items.basetime)		
		upperindex = items.locate_index(uppertime) - 1
		upperindexvalue = items.unixtime[upperindex]
		baseindexvalue = items.unixtime[baseindex]
		string += 'Base: {0} [{1}], Upper: {2} [{3}]\n'.format(baseindexvalue, baseindex, upperindexvalue, upperindex)
		string += 'Number of items in sublist: {0}'.format(len(items.unixtime[baseindex:upperindex]) + 1)
		
		# do some processing
		# put your statistics function here
		if (verbose): print string
		append_string_to_out('\n' + string + '\n', stat_file)

		count_oncampus_occurences(items.filtered_items[baseindex:upperindex])
		items.ranking(baseindex, upperindex)
		items.unique_content(baseindex, upperindex)
				
		# checks if timeslice is the last one
		# ends loop if timeslice reaches EOL
		if x == timeslices-1: break
		else: items.basetime = uppertime
		iter += 1

def dumpstring(items):
	csv_string = ''
	for i in range(len(items.filtered_items)):  		
		csv_string += items.ip[i] + ', '
		csv_string += items.name[i] + ', '
		csv_string += items.date[i] + ', '
		csv_string += items.tzone[i] + ', '
		csv_string += (str(items.unixtime[i])) + ', '
		csv_string += items.request[i] + ', '
		csv_string += items.bytes[i] + '\n'
		items.parsed = csv_string
	return items.parsed

def dump_string_to_out(string, filename):
	file = open(filename, 'w')
	file.write(string)
	file.close()

def append_string_to_out(string, filename):
	file = open(filename, 'a')
 	file.write(string)
 	file.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
		'--in_file','-f',
		type = str,
		help = 'Use custom input file',
		default = 'data.log'
	)
	parser.add_argument(
		'--out_file','-o',
		type = str,
		help = 'Use custom output file',
		default = 'parsed.csv'
	)
	parser.add_argument(
		'--stat_file','-s',
		type = str,
		help = 'Use custom statistics file',
		default = 'stat.csv'
	)
	parser.add_argument(
		'--keyword','-k',
		type = str,
		help = 'Specify keyword',
		default = '.pdf'
	)
	parser.add_argument(
		'--timewindow','-t',
		type = int,
		help = 'Specify timewindow',
		default = 14400
	)
	parser.add_argument(
		'--oncampaddr','-ipc',
		type = str,
		help = 'Specify campus ip address',
		default = '10.?'
	)	
	parser.add_argument(
		'--verbose','-v',
		action = 'store_true',
		help = 'Print verbose conversions',
	)
	parser.add_argument(
		'--genstat','-gs',
		action = 'store_true',
		help = 'Generate statistical report',
	)	
	args = parser.parse_args()	
	# passes arguments to global namespace:
	globals().update(args.__dict__)
	main(
		in_file = args.in_file,
		out_file = args.out_file,
		stat_file = args.stat_file,
		keyword = args.keyword,
		timewindow = args.timewindow
)