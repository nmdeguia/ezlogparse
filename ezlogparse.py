# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab #

import sys
from collections import Counter
import time
import datetime
import re
import bisect
import argparse

#script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.?' # ip_address of campus networks
timewindow = 14400
debug = 'nice, that line is correct'
# just a debug string
# print whenever needed

def main(in_file, out_file, keyword):
	items = parse_ezlog(in_file)
	temp = items.search(keyword)
	items.extract()
	items.dt_to_unix_timestamp()
	items.dumpstring()
	items.csvdump(out_file)

	items.count_occurences()
	items.count_oncampus_occurences(temp)

	items.generate_statistics()

class parse_ezlog(object):

	def __init__(self, in_file):
		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]	#used in search function
		f.close()

		self.filtered_items = list()	#used in search function
		#self.gen_filtered_items = list()
		
		self.ip = list()		#0
		self.name = list()		#2
		self.datetime = list()	#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		self.parsed = list()
		self.unixtime = list()
		self.prev_basetime = 0
		self.prev_uppertime = 0	
		self.prev_index = 0

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
			self.datetime.append(self.filtered_items[i][3].strip('['))
			self.tzone.append(self.filtered_items[i][4].strip(']'))
			self.request.append(self.filtered_items[i][6])
			self.bytes.append(self.filtered_items[i][9])			

	def dumpstring(self):
  		csv_string = ""  		
		for i in range(len(self.filtered_items)):  		
 			csv_string += self.ip[i] + ', '
			csv_string += self.name[i] + ', '
			csv_string += (str(self.unixtime[i])) + ', '
			csv_string += self.request[i] + ', '
			csv_string += self.bytes[i] + '\n'
			self.parsed = csv_string
		return self.parsed
	
	def csvdump(self, out_file):
		out_file = open(out_file, 'w')
		out_file.write(self.parsed)
		out_file.close()
			
	def csvappend(self, out_file):
		out_file = open(out_file, 'a')
		out_file.write(self.parsed)
		out_file.close()
			
	def count_occurences(self):		
		self.ip_count = Counter(self.ip)
		self.name_count = Counter(self.name)
		self.datetime_count = Counter(self.datetime)
		self.tzone_count = Counter(self.tzone)
		self.request_count = Counter(self.request)
		
		#print "Number of Occurences: Corresponding IP Address"
		#for letter, count in self.ip_count.most_common():
		#	print "{1} : {0}".format(letter, count)
		
		#print "Number of Occurences: Corresponding Names"
		#for letter, count in self.name_count.most_common():
		#	print "{1} : {0}".format(letter, count)

	def count_oncampus_occurences(self, data_in):
		on_campus_count = 0
		off_campus_count = 0   		
		for i in range(len(data_in)):
			if data_in[i][0].startswith(on_campus_ipaddr):
				on_campus_count += 1
			else:
				off_campus_count += 1
		print "Number of on-campus accesses: {0}".format(on_campus_count)
		print "Number of off-campus accesses: {0}".format(off_campus_count)

	def count_item_occurences(self, data_in):
    	#for i in range(len(data_in)):
		#print(data_in[0])
		pass

	def dt_to_unix_timestamp(self):
		for x in range(len(self.datetime)):
			dt = re.split(r"[[/:]+", self.filtered_items[x][3])
			dt[2] = time.strptime(dt[2], '%b').tm_mon # month to number
			dt.pop(0) # remove blank element from start of list
			dt = list(map(int, dt))
			tz = int(self.tzone[x][2:])
			# convert dt to unix timestamp:
			# parameters are: yr,mo,day,hr,min,sec,tz outputs float
			temp = datetime.datetime(dt[2],dt[1],dt[0],dt[3],dt[4],dt[5],tz)			
			self.unixtime.append(int(time.mktime(temp.timetuple())))
		print(self.unixtime[0])
		return self.unixtime

	def locate_index(self, timelookup):
    	# locates the nearest number it first encounters
		# returns index
    		index = bisect.bisect_left(self.unixtime,timelookup)
		return int(index)

	def get_slice_timewindow(self, prev):
    	# sets new basetime based on the previous one
		# initializes basetime to first element in unixtime
		if self.prev_basetime is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = self.prev_basetime
		return new_basetime

	def generate_statistics(self):
 		print "---------------------------".format() 
		print "Generating Statistics".format()  		
		print "EOL: {0}".format(len(self.filtered_items)) # End of line	
		print "Initial timestamp: {0}".format(self.unixtime[0])	
		print "Last timestamp: {0}".format(self.unixtime[len(self.unixtime)-1])
		iter = 1
		finaltime = self.unixtime[len(self.unixtime)-1]
		elapsedtime = finaltime - self.unixtime[0]
		timeslices = int(elapsedtime/timewindow)
		print "Time diff: {0}".format(elapsedtime)
		print "Timewindow: {0}".format(timewindow)
		print "Total timeslices: {0}".format(timeslices)
		for x in range(timeslices):
			print "---------------------------".format()
			print "Timeslice #{0}".format(iter)
			basetime = self.get_slice_timewindow(self.prev_basetime)
			uppertime = basetime + timewindow
			baseindex = self.locate_index(basetime)		
			upperindex = self.locate_index(uppertime)
			print "base: {0} [{1}], upper: {2} [{3}]".format(basetime, baseindex, uppertime, upperindex)
			print "Number of items in sublist: {0}".format(len(self.unixtime[baseindex:upperindex]))
			# do some processing
			# put your statistics function here
			self.count_oncampus_occurences(self.filtered_items[baseindex:upperindex])
			self.count_item_occurences(self.filtered_items[baseindex:upperindex])
			# checks if timeslice is the last one
			# ends loop if timeslice reaches EOL
			if iter == timeslices-1: break
			else: self.prev_basetime = self.unixtime[upperindex+1]
			iter += 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument(
        '--in_file','-f',
		type = str,
        help = 'Use custom input file',
        default = 'data-small'
    )
	parser.add_argument(
        '--out_file','-o',
		type = str,
        help = 'Use custom output file',
        default = 'parsed-out.csv'
    )
	parser.add_argument(
        '--keyword','-k',
		type = str,
        help = 'Specify keyword',
        default = '.pdf'
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
		keyword = args.keyword
	)