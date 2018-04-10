from sys import argv

script, in_file, out_file = argv

def niceprint(list):
	print '--------------------' #20
	for i in list:
		print i
	print '------------------------------------------------------------' #60
	return

def strprintln(string):
	print '++++++++++++++++++++' #20
	print string.split('\n')
	print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++' #60
	return
	
class EZlog(object):

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
		self.csv_string = ""
		self.parsed = list()
		
	def search(self, keyword):
		#self.lookup = list()	#reinitialize lookup list
		for i in range(len(self.str_split)):
			if keyword in self.str_split[i][0]:			#search within ip
				self.lookup.append(self.str_split[i])
		for i in range(len(self.str_split)):
			if keyword in self.str_split[i][2]:			#search within name
				self.lookup.append(self.str_split[i])
		for i in range(len(self.str_split)):
			if keyword in self.str_split[i][3]:			#search within date
				self.lookup.append(self.str_split[i])
		for i in range(len(self.str_split)):
			if keyword in self.str_split[i][4]:			#search within tzone
				self.lookup.append(self.str_split[i])
		for i in range(len(self.str_split)):
			if keyword in self.str_split[i][6]:			#search within request
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
			
	def analyze(self):
		pass
			
a = EZlog(in_file)
b = EZlog(in_file)
c = EZlog(in_file)

print 'this is raw of a'
#niceprint(a.raw)

print 'this is lookup of a'
a.search('.pdf')
#niceprint(a.search('.pdf'))

#b.search('BARTON')
#c.search('86.55.237.139')

#print 'this is str_split of a'
#niceprint(a.str_split)

a.extract()
#b.extract()
#c.extract()

#print 'this is csv_string of a'
#print a.csv_string

a.csvdump()
#b.csvappend()
#c.csvappend()