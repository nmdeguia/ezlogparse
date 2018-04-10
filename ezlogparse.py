from sys import argv
from collections import Counter

script, in_file, keyword, out_file = argv

on_campus_ipaddr = '10.'

def niceprint(list):
	print '--------------------' #20
	for i in list:
		print i
	print '------------------------------------------------------------' #60
	return
	
class parse_ezlog(object):
	
	def __init__(self, in_file):
		self.in_file = open(in_file, 'r')
		self.raw = list(self.in_file)
		self.in_file.close()

		with open(in_file, 'r') as f:
			self.str_split = [i.split() for i in f]	#used in search function
		
		self.lookup = list()	#used in search function
		#self.gen_lookup = list()
		
		self.ip = list()		#0
		self.name = list()		#2
		self.date = list()		#3[
		self.tzone = list()		#4]
		self.request = list()	#6
		self.bytes = list()		#7
		self.csv_string = ""
		self.parsed = list()
		
	def search(self, keyword):
		for i in range(len(self.str_split)):
			for j in range(7):	#search all fields
				if keyword in self.str_split[i][j]:
					self.lookup.append(self.str_split[i])
		return self.lookup
		
	def extract(self):
		for i in range(len(self.lookup)):
			self.ip.append(self.lookup[i][0])
			self.name.append(self.lookup[i][2])
			self.date.append(self.lookup[i][3].strip('['))
			self.tzone.append(self.lookup[i][4].strip(']'))
			self.request.append(self.lookup[i][6])
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
		for i in range(len(self.str_split)):
			if on_campus_ipaddr in self.str_split[i][0]:
				on_campus_count += 1
			else:
				off_campus_count += 1
		print("Number of on campus accesses: %i" % on_campus_count)
		print("Number of off campus accesses: %i" % off_campus_count)

items = parse_ezlog(in_file)
filtered_items = parse_ezlog(out_file)

#print 'this is raw of a'
#niceprint(a.raw)

#print 'this is lookup of a'
items.search(keyword)
#niceprint(a.search('.pdf'))
#b.search('BARTON')
#c.search('86.55.237.139')

#print 'this is str_split of a'
#niceprint(a.str_split)

items.extract()
#b.extract()
#c.extract()

#print 'this is csv_string of a'
#print a.csv_string

items.csvdump()
#b.csvappend()
#c.csvappend()

items.count_occurences()
filtered_items.count_oncampus_occurences()
#print "Class Counter"
#print Counter(a.ip)
#print "List Counter"
#print list(Counter(a.ip))
#print "--------------------------------------------------"
#print a.ip_count
#print type(a.ip_count)

#print items.ip_count
#print a.name_count
#print a.date_count
#print a.tzone_count
#print a.request_count

#print "The most common IP is {}".format(a.ip_count.most_common().pop(0))
#print type(a.ip_count.most_common().pop(0))
