# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab #

from sys import argv
from collections import Counter
from bisect import bisect_left
import time
import datetime
import re

script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.?' # ip_address of campus networks
timewindow = 14400	# 1 day = 86400s
debug = 'nice, that line is correct'
# just a debug string
# print whenever needed

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
	
	def csvdump(self):
		file = open(out_file, 'w')
		file.write(self.parsed)
		file.close()
			
	def count_occurences(self):		
		self.ip_count = Counter(self.ip)
		self.name_count = Counter(self.name)
		self.date_count = Counter(self.date)
		self.tzone_count = Counter(self.tzone)
		self.request_count = Counter(self.request)
		self.byte_count = Counter(self.byte)
		
		self.ip_ranked = self.ip_count.most_common()
		self.name_ranked = self.name_count.most_common()
		self.date_ranked = self.date_count.most_common()
		self.tzone_ranked = self.tzone_count.most_common()
		self.request_ranked = self.request_count.most_common()
		self.byte_ranked = self.byte_count.most_common()
				
	def ranking(self, data_count, a, b):
		print debug
		counta = 0
		for i in range(len(data_count)):
			ip = Counter(data_count[a:b][0])
			name = Counter(data_count[a:b][2])
			date = Counter(data_count[a:b][3])
			tzone = Counter(data_count[a:b][4])
			request = Counter(data_count[a:b][6])
			#byte = Counter(data_count[a:b][9])
			for x in ip.most_common(1): counta += 1
			#for i in name.most_common(1): print i
			#for i in date.most_common(1): print i
			#for i in tzone.most_common(1): print i
			#for i in request.most_common(1): print i
			#print ip
		print counta	
		#return ip, name, date, tzone, request
		
	def ranking2(self, data_count):
		self.ranks = Counter(data_count)
		for i in a.ranks.most_common(): print i

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

	def locate_index(self, timelookup):	# locates the nearest number it first encounters    	
		index = bisect_left(self.unixtime,timelookup)	# returns index
		return int(index)
		
	def get_slice_timewindow(self, time):
		if time is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = time
		print "({} - {})".format(new_basetime, new_basetime + timewindow)
		return new_basetime
		
	def generate_statistics(self):
		finaltime = self.unixtime[len(self.unixtime)-1]
		elapsedtime = finaltime - self.unixtime[0]
		#print elapsedtime
		timeslices = (elapsedtime/timewindow)+1
		
 		print "---------------------------".format() 
		print "Generating Statistics...".format()  			
		print "Initial timestamp: {0} [{1}]".format(self.unixtime[0], 0)	
		print "Last timestamp: {0} [{1}]".format(self.unixtime[len(self.unixtime)-1], len(self.unixtime) - 1)
		print "Total Number of Items: {}".format(len(self.unixtime))
		print "Number of Time slices: {}.".format(timeslices)
		print "Per Time slice: {} seconds.".format(timewindow)
		iter = 1
		for x in range(timeslices):
			print "---------------------------".format()
			print "Timeslice #{0}".format(iter),
			basetime = self.get_slice_timewindow(self.basetime)
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
			#self.ranking(self.filtered_items, baseindex, upperindex)

			# checks if timeslice is the last one
			# ends loop if timeslice reaches EOL
			if x == timeslices-1: break
			else: self.basetime = uppertime
			iter += 1
		
a = parse_ezlog(in_file)
a.search(keyword)
a.extract()
a.dt_to_unix_timestamp()
a.dumpstring()
a.csvdump()
a.generate_statistics()
#a.ranking2(Counter(a.ip))