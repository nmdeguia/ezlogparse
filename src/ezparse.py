import re
import time, datetime
from bisect import bisect_left
from collections import Counter

class parse_ezlog(object):
	def __init__(self, in_file):

		with open(in_file, 'r') as f:
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
				# if (verbose): print(self.string[-1])
			self.string.append('Number of Unique URLs: {0}'.format(len(set(temp))))
			# if (verbose): print(self.string[-1])

		for i, j in enumerate(unique, 1):
			self.string.append('IP{0}: {0}\nURL{0}: {0}'.format(i, j[0], i, j[1]))

		self.string.append('Number of Unique IP: {0}'.format(len(list(unique))))
		# if (verbose): print(self.string[-1])
		return list(unique)

	def unique_sites(self, a, b):
		pass

	def final_content(self):
		temp = list(zip(self.ip, self.name, self.date, self.tzone,
			list(map(str, self.unixtime)), self.request, self.bytes))
		for i in self.indices:
			self.content.append(temp[i])
