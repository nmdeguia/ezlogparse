from sys import argv
from collections import Counter
import time
import datetime
import re

script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.?' # ip_address of campus networks
timewindow = 86400
debug = 'nice, that line is correct'
# just a debug string
# print whenever needed

class parse_ezlog(object):
	
	def __init__(self, in_file):
		self.in_file = open(in_file, 'r')
		self.raw = list(self.in_file)
		self.in_file.close()

		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]	#used in search function
		
		self.filtered_items = list()	#used in search function
		#self.gen_filtered_items = list()
		
		self.ip = list()		#0
		self.name = list()		#2
		self.datetime = list()	#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		self.csv_string = ""
		self.parsed = list()
		self.unixtime = list()
		self.prev_basetime = 0
		self.prev_uppertime = 0	

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
		for i in range(len(self.filtered_items)):  		
 			self.csv_string += self.ip[i] + ', '
			self.csv_string += self.name[i] + ', '
			self.csv_string += (str(self.unixtime[i]))[:-2] + ', '
			self.csv_string += self.request[i] + ', '
			self.csv_string += self.bytes[i] + '\n'
			self.parsed = self.csv_string
		return self.parsed   		
	
	def csvdump(self):
		self.out_file = open(out_file, 'w')
		self.out_file.write(self.parsed)
		self.out_file.close()
			
	def csvappend(self):
		self.out_file = open(out_file, 'a')
		self.out_file.write(self.parsed)
		self.out_file.close()
			
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

	def count_oncampus_occurences(self):
		on_campus_count = 0
		off_campus_count = 0   		
		for i in range(len(self.filtered_items)):
			if self.filtered_items[i][0].startswith(on_campus_ipaddr):
				on_campus_count += 1
			else:
				off_campus_count += 1
		print "Number of on-campus accesses: {0}".format(on_campus_count)
		print "Number of off-campus accesses: {0}".format(off_campus_count)

	def dt_to_unix_timestamp(self):
		for x in range(len(self.datetime)):
			dt = re.split(r"[[/:]+", self.filtered_items[x][3])
			# print "date : month : year : 24-hour-time : minute : seconds"	
			dt[2] = time.strptime(dt[2], '%b').tm_mon
			dt.pop(0) # remove blank element from start of list
			yr = int(dt[2])
			mo = int(dt[1])
			day = int(dt[0])
			hr = int(dt[3])
			min = int(dt[4])
			sec = int(dt[5])
			tz = int(self.tzone[x][2:])
			# convert dt to unix timestamp:
			dt_temp = datetime.datetime(yr,mo,day,hr,min,sec,tz)
			self.unixtime.append(int(time.mktime(dt_temp.timetuple())))
		return self.unixtime

	def get_slice_timewindow(self, prev):
		if self.prev_basetime is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = self.prev_basetime
		print "prev: {0}".format(new_basetime)
		return new_basetime

	def get_statistics(self):
		basetime = self.get_slice_timewindow(self.prev_basetime)
		uppertime = basetime + timewindow
		print "base: {0}, upper: {1}".format(basetime, uppertime)
		# do some processing
		self.prev_basetime = uppertime


items = parse_ezlog(in_file)
items.search(keyword)
items.extract()
items.dt_to_unix_timestamp()
items.dumpstring()
items.csvdump()

items.count_occurences()
items.count_oncampus_occurences()

items.get_statistics()
