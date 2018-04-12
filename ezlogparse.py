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
		#self.gen_filtered_items = list()
		
		self.ip = list()		#0
		self.name = list()		#2
		self.date = list()		#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		
		self.slice_value = list()
		self.difference = list()
		self.slice_count = 0
		self.parsed = list()
		self.unixtime = list()
		self.basetime = 0
		self.finaltime = 0
		self.index_list = list()
		self.pos_index = 0
		
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
			
	def csvappend(self):
		file = open(out_file, 'a')
		file.write(self.parsed)
		file.close()
			
	def count_occurences(self):		
		self.ip_count = Counter(self.ip)
		self.name_count = Counter(self.name)
		self.date_count = Counter(self.date)
		self.tzone_count = Counter(self.tzone)
		self.request_count = Counter(self.request)
		
		self.ip_ranked = self.ip_count.most_common()
		self.name_ranked = self.name_count.most_common()
		self.date_ranked = self.date_count.most_common()
		self.tzone_ranked = self.tzone_count.most_common()
		self.request_ranked = self.request_count.most_common()
		
	def ranking(self, data_count):
		self.ranks = Counter(data_count)
		return self.ranks.most_common()

	def count_oncampus_occurences(self):
		on_campus_count = 0
		off_campus_count = 0   		
		for i in range(len(self.ip)):
			if self.ip[i].startswith(on_campus_ipaddr):
				on_campus_count += 1
			else:
				off_campus_count += 1
		print "Number of on-campus accesses: {}".format(on_campus_count)
		print "Number of off-campus accesses: {}".format(off_campus_count)

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
		
	def get_slice_timewindow(self, time):
		if time is 0:
			new_basetime = self.unixtime[0]
		else: new_basetime = time
		print "Basetime is = {0}".format(new_basetime)
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

	def get_timeslices(self):
		self.basetime = self.unixtime[0]
		self.finaltime = self.unixtime[len(self.unixtime)-1]
		elapsed_time = self.finaltime - self.basetime
		self.timeslices = (elapsed_time/timewindow) + 2
		print "Basetime: {} seconds".format(self.basetime)
		print "Finaltime: {} seconds".format(self.finaltime)
		print "Time Elapsed: {} seconds".format(elapsed_time)
		print "Number of Time slices: {}.".format(self.timeslices -1)
		print "Per Time slice: {} seconds.".format(timewindow)
		print "------------------------------------------------------------" #60

		self.slice_count = range(self.timeslices)
		
		for i in range(self.timeslices):
			self.slice_count[i] = self.basetime + timewindow
			self.slice_count[i] += (timewindow*(i))
			self.index_list.append(str(self.pos_index))
			self.index_list = map(int, self.index_list)
			self.takeClosest(self.unixtime, self.slice_count[i])
			self.slice_value.append(self.unixtime[self.pos_index])
			self.difference = [self.index_list[j+1] - self.index_list[j] for j in range(len(self.index_list)-1)]
		
		self.slice_count.pop()
		#self.slice_count.insert(0, self.basetime)
		self.index_list.pop(0)
		#self.difference.pop(0)
		print self.timeslices
		print self.slice_value
		#print self.slice_count	#print boundaries of timewindows
		print self.index_list
		print self.difference
		#self.difference.reverse()
		#print self.difference
		#print self.difference.pop()
		print "------------------------------------------------------------" #60
		
		counta = 0
		temp = 0
		kounta = 0
		#for i in range(self.timeslices):
		for j in self.index_list:
			print "Timeslice {} is {}".format(counta, self.basetime + (timewindow*counta))
			counta += 1
			#print self.unixtime[temp:j]]
			tempList = self.unixtime[temp:j+1]
			for i in tempList: print i
			print len(tempList)
			temp=j
			print "------------------------------------------------------------" #60
	
	def takeClosest(self, myList, myNumber):
		#Assumes myList is sorted. Returns closest value to myNumber.
		#If two numbers are equally close, return the smallest number.
		self.pos_index = bisect_left(myList, myNumber)
		#print "Current pos is {} and value is compared to {}".format(self.pos_index, myNumber)
		if self.pos_index == 0:
			return self.pos_index
		if self.pos_index == len(myList):
			#print "Last item for this timewindow is: {1} at pos: {0}".format(self.pos_index, myList[-1])
			#print "Pos is max ({}) at {}".format(self.pos_index, myList[-1])
			self.pos_index -= 1
			return self.pos_index
		Last = myList[self.pos_index - 1]
		Next = myList[self.pos_index]
		self.pos_index -= 1
		return self.pos_index
		
		#print "Last in this timewindow {}".format(Last)
		#print "Next after this timewindow {}".format(Next)
		
	def extract2(self, data, ip, name, date, tzone, request, bytes):
		for i in range(len(data)):
			ip.append(data[i][0])
			name.append(data[i][2])
			date.append(data[i][3].strip('['))
			tzone.append(data[i][4].strip(']'))
			request.append(data[i][6])
			bytes.append(data[i][9])
		return (ip, name, date, tzone, request, bytes)
		
a = parse_ezlog(in_file)
a.search(keyword)
#a.extract(a.filtered_items, a.ip, a.name, a.date, a.tzone, a.request, a.bytes)
a.extract()
a.dt_to_unix_timestamp()
a.dumpstring()
a.csvdump()
a.count_occurences()
a.count_oncampus_occurences()
a.get_timeslices()
#a.between_slices()