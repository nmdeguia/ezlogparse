# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab #

from sys import argv
from collections import Counter
from bisect import bisect_left
import time
import datetime
import re
import argparse

on_campus_ipaddr = '10.?' # ip_address of campus networks
global timewindow #14400	# 1 day = 86400s, 12 hours = 43200s, 6 hours = 21600, 
debug = 'nice, that line is correct'
# just a debug string
# print whenever needed

def main(in_file, out_file, stat_file, keyword, timewindow):
	data = parse_ezlog(in_file)
	data.search(keyword)
	data.extract()
	data.dt_to_unix_timestamp()
	data.dumpstring()
	data.csvdump(out_file)	
	data.generate_statistics(timewindow)
	data.statdump(stat_file, data.str_stat)
	
class parse_ezlog(object):
	
	def __init__(self, in_file):
		file = open(in_file, 'r')
		raw = list(in_file)
		file.close()

		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]	#used in search function
		
		self.filtered_items = list()	#used in search function
		
		self.ip = list()		#0
		self.name = list()		#2
		self.date = list()		#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		
		self.str_stat = list()
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

	def dumpstring(self):
  		csv_string = ""  		
		for i in range(len(self.filtered_items)):  		
 			csv_string += self.ip[i] + ', '
			csv_string += self.name[i] + ', '
			csv_string += self.date[i] + ', '
			csv_string += self.tzone[i] + ', '
			csv_string += (str(self.unixtime[i])) + ', '
			csv_string += self.request[i] + ', '
			csv_string += self.bytes[i] + '\n'
			self.parsed = csv_string
		return self.parsed
	
	def statdump(self, stat_file, string):
		file = open(stat_file, 'w')
		file.write(string)
		file.close()
		
	def csvdump(self, out_file):
		file = open(out_file, 'w')
		file.write(self.parsed)
		file.close()
		
	def ranking(self, a, b):
		count = 0
		print "Count of duplicate URLs:"
		self.request_count = Counter(self.request[a:b+1])
		for i in self.request_count.most_common():
			count += 1
			print "Content ID: {0}, Number of requests: {1}".format(count, i[1])

	def unique_content(self, a, b):
		count = 0
		#self.unique = Counter(set(zip(self.name[a:b+1], self.request[a:b+1])))
		self.unique = set(self.request[a:b+1])
		for i in self.unique:
			count += 1
			#print "Unique Name: {}, Unique URL: {}".format(i[0], i[1])
			#print "Unique URL: {}".format(i)
		print "Number of Unique URL: {}".format(count)
		#self.unique_index(a, b)
		
	def unique_index(self, a, b):
		pass
		#count = 0
		#for i in range(len(self.request[a:b+1])):
			#count += 1
		#print count
	
	def count_oncampus_occurences(self, data_in):
		on_campus_count = 0
		off_campus_count = 0   		
		for i in range(len(data_in)):
			if data_in[i][0].startswith(on_campus_ipaddr):
				on_campus_count += 1
			else:
				off_campus_count += 1
		print "Number of on-campus accesses: {0}".format(on_campus_count)
		print "Number of off-campus accesses: {0}".format(off_campus_count + 1)

	def dt_to_unix_timestamp(self):
		for i in range(len(self.date)):
			dt = re.split(r"[[/:]+", self.filtered_items[i][3])
			dt[2] = time.strptime(dt[2], '%b').tm_mon # month to number
			dt.pop(0) # remove blank element from start of list
			dt = list(map(int, dt))
			tz = int(self.tzone[i][2:])
			# convert dt to unix timestamp:
			# dt_temp = date.datetime(yr,mo,day,hr,min,sec,tz) = float
			temp = datetime.datetime(dt[2],dt[1],dt[0],dt[3],dt[4],dt[5],tz)			
			self.unixtime.append(int(time.mktime(temp.timetuple())))
		#print "Temp date is = {}".format(temp)
		#print "Base time is: {}".format(self.unixtime[0])
		return self.unixtime

	def locate_index(self, timelookup):	# locates the nearest number to the left of timelookup    	
		index = bisect_left(self.unixtime,timelookup)	# returns index
		return int(index)
		
	def get_slice_timewindow(self, time, timewindow):
		if time is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = time
		print "({} - {})".format(new_basetime, new_basetime + timewindow)
		return new_basetime
		
	def generate_statistics(self, timewindow):
		finaltime = self.unixtime[len(self.unixtime)-1]
		elapsedtime = finaltime - self.unixtime[0]
		timeslices = (elapsedtime/timewindow)+1
		
 		print "--------------------------------------------------"
		print "Generating Statistics..."
		self.str_stat = "Initial timestamp: {0} [{1}]".format(self.unixtime[0], 0) + "\n"
		self.str_stat += "Last timestamp: {0} [{1}]".format(self.unixtime[len(self.unixtime)-1], len(self.unixtime) - 1) + "\n"
		self.str_stat += "Total Number of Items: {}".format(len(self.unixtime))  + "\n"
		self.str_stat += "Number of Time slices: {}.".format(timeslices) + "\n"
		self.str_stat += "Per Time slice: {} seconds.".format(timewindow) + "\n"
		
		print self.str_stat
		
		iter = 1
		for x in range(timeslices):
			print "--------------------------------------------------".format()
			print "Timeslice #{0}".format(iter),
			basetime = self.get_slice_timewindow(self.basetime, timewindow)
			uppertime = basetime + timewindow
			baseindex = self.locate_index(basetime)		
			upperindex = self.locate_index(uppertime) - 1
			upperindexvalue = self.unixtime[upperindex]
			baseindexvalue = self.unixtime[baseindex]
			print "Base: {0} [{1}], Upper: {2} [{3}]".format(baseindexvalue, baseindex, upperindexvalue, upperindex)
			print "Number of items in sublist: {0}".format(len(self.unixtime[baseindex:upperindex]) + 1)
			# do some processing
			# put your statistics function here
			self.count_oncampus_occurences(self.filtered_items[baseindex:upperindex])
			self.ranking(baseindex, upperindex)
			self.unique_content(baseindex, upperindex)

			# checks if timeslice is the last one
			# ends loop if timeslice reaches EOL
			if x == timeslices-1: break
			else: self.basetime = uppertime
			iter += 1
		
if __name__ == '__main__':
    	parser = argparse.ArgumentParser()
	parser.add_argument(
        '--in_file','-f',
		type = str,
        help = 'Use custom input file',
        default = 'data-small.log'
    )
	parser.add_argument(
        '--out_file','-o',
		type = str,
        help = 'Use custom output file',
        default = 'parsed-out.csv'
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
        '--timewindow','-tw',
		type = int,
        help = 'Specify timewindow',
        default = 14400
    )
	parser.add_argument(
		'--verbose','-v',
		action = 'store_true',
        help = 'Print verbose conversions',
    )	
	args = parser.parse_args()	
	main(
		in_file = args.in_file,
		out_file = args.out_file,
		stat_file = args.stat_file,
		keyword = args.keyword,
		timewindow = args.timewindow
)