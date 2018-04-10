from sys import argv
from collections import Counter

script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.?' # ip_address of campus networks

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
		self.date = list()		#3[
		self.tzone = list()		#4]
		self.request = list()		#6
		self.bytes = list()		#7
		self.csv_string = ""
		self.parsed = list()
		
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
			self.csv_string += self.ip[i] + ', '
			self.csv_string += self.name[i] + ', '
			self.csv_string += self.date[i] + ', '
			self.csv_string += self.tzone[i] + ', '
			self.csv_string += self.request[i] + '\n'
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
		self.date_count = Counter(self.date)
		self.tzone_count = Counter(self.tzone)
		self.request_count = Counter(self.request)
		
		print "Number of Occurences: Corresponding IP Address"
		for letter, count in self.ip_count.most_common():
			print "{1} : {0}".format(letter, count)
		
		print "Number of Occurences: Corresponding Names"
		for letter, count in self.name_count.most_common():
			print "{1} : {0}".format(letter, count)

	def count_oncampus_occurences(self):
		on_campus_count = 0
		off_campus_count = 0   		
		for i in range(len(self.filtered_items)):
			if on_campus_ipaddr in self.filtered_items[i][0]:
				on_campus_count += 1
			else:
				off_campus_count += 1
		print "Number of on campus accesses: {0}".format(on_campus_count)
		print "Number of on campus accesses: {0}".format(off_campus_count)

	def convert_dt_to_seconds():
		pass

items = parse_ezlog(in_file)
items.search(keyword)
items.extract()
items.csvdump()

items.count_occurences()
items.count_oncampus_occurences()
