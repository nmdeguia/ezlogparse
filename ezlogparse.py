# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab #

from sys import argv
from collections import Counter
import time
import datetime
import re

script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.?' # ip_address of campus networks
timewindow = 86400/60
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
  		csv_string = ""  		
		for i in range(len(self.filtered_items)):  		
 			csv_string += self.ip[i] + ', '
			csv_string += self.name[i] + ', '
			csv_string += (str(self.unixtime[i])) + ', '
			csv_string += self.request[i] + ', '
			csv_string += self.bytes[i] + '\n'
			self.parsed = csv_string
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

	def dt_to_unix_timestamp(self):
		for x in range(len(self.datetime)):
			dt = re.split(r"[[/:]+", self.filtered_items[x][3])
			dt[2] = time.strptime(dt[2], '%b').tm_mon # month to number
			dt.pop(0) # remove blank element from start of list
			dt = list(map(int, dt))
			tz = int(self.tzone[x][2:])
			# convert dt to unix timestamp:
			# dt_temp = datetime.datetime(yr,mo,day,hr,min,sec,tz) = float
			temp = datetime.datetime(dt[2],dt[1],dt[0],dt[3],dt[4],dt[5],tz)			
			self.unixtime.append(int(time.mktime(temp.timetuple())))
		print(self.unixtime[0])
		return self.unixtime

	# not working yet
	def locate_index(self, str_lookup):
		#return self.unixtime.index(int(str_lookup))
		pass

	def get_slice_timewindow(self, prev):
		if self.prev_basetime is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = self.prev_basetime
		print "prev: {0}".format(new_basetime)
		return new_basetime

	def generate_statistics(self):
 		print "---------------------------".format() 
		print "Generating Statistics".format()  		
		print "EOL: {0}".format(len(self.filtered_items)) # End of line	
		print "Initial timestamp: {0}".format(self.unixtime[0])	
		print "Last timestamp: {0}".format(self.unixtime[len(self.unixtime)-1])
		iter = 1
		#while True:
		for x in range(2):
			print "---------------------------".format()
			print "Timeslice #{0}".format(iter)
			basetime = self.get_slice_timewindow(self.prev_basetime)
			uppertime = basetime + timewindow
			baseindex = self.locate_index(basetime)		
			upperindex = self.locate_index(uppertime)
			# check if upperindex is end of data
			#if upperindex > len(self.filtered_items):
    		#		break
			#else: pass
			#print "base: {0} [{1}], upper: {2} [{3}]".format(basetime, baseindex, uppertime, upperindex)
			print "base: {0}, upper: {1}".format(basetime, uppertime)			
			# do some processing
			self.count_oncampus_occurences(self.filtered_items[baseindex:upperindex])
			self.prev_basetime = uppertime
			iter += 1


items = parse_ezlog(in_file)
temp = items.search(keyword)
items.extract()
items.dt_to_unix_timestamp()
items.dumpstring()
items.csvdump()

items.count_occurences()
items.count_oncampus_occurences(temp)

items.generate_statistics()
