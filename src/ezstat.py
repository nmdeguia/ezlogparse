# vim: set tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab
#
# Authors:
#	Bandiola, Al Tristan
#	de Guia, Norman Roy
#
# This script is made specifically for the analysis of ezproxy logs,
# which would later be used for the completion of our capstone project.
#
# Usage: $ python ezlogparse.py --argument value
#
# More details in github.com/nmdeguia/ezlogparse/README.md

import datetime
import ipaddress
import numpy as np

from src import ezparse
from src import ezplot

def generate(args, global_data, items, flag):
	# update args globally
	globals().update(args.__dict__)
	# set initial value of lowerbound index to 0 in the first iteration
	basetime = items.unixtime[0]
	finaltime = items.unixtime[-1]
	elapsedtime = finaltime - items.unixtime[0]
	timeslices = int((elapsedtime/timewindow)+1)

	print('Generating Statistics')
	print('Initial timestamp: {0} [{1}]'.format(items.unixtime[0], 0))
	print('Final timestamp: {0} [{1}]'.format(finaltime, len(items.unixtime)-1))
	print('Per time slice: {0} seconds.'.format(timewindow))
	# print('Total number of items: {0}'.format(len(items.unixtime)))
	print('Number of time slices: {0}'.format(timeslices))

	if (flag == 0): mode = 'w'
	else: mode = 'a'

	for iter, x in enumerate(range(timeslices),1):
		if (verbose): print('--------------------------------------------------')

		items.string.append('Timeslice no. {0} ({1} - {2})'.format(
			iter, basetime, basetime+timewindow))
		if (verbose): print(items.string[-1])

		# initialize time slice indices
		uppertime = basetime + timewindow
		baseindex = items.locate_index(basetime)

		# set ceiling value for uppertime
		if uppertime >= items.unixtime[-1]: uppertime = items.unixtime[-1]
		upperindex = items.locate_index(uppertime)

		if upperindex != baseindex:
			#length = len(items.unixtime[baseindex:upperindex])
			if (x != timeslices-1): upperindex -= 1
			else: upperindex = items.locate_index(uppertime)
		# else: length = 0

		# get unixtime value of upperbound and lowerbound indices
		baseindexvalue = items.unixtime[baseindex]
		upperindexvalue = items.unixtime[upperindex]

		items.string.append('{0} to {1}'.format(
			datetime.datetime.fromtimestamp(
				int(baseindexvalue)).strftime('%Y-%m-%d %H:%M:%S'),
			datetime.datetime.fromtimestamp(
				int(upperindexvalue)).strftime('%Y-%m-%d %H:%M:%S')
			))
		if (verbose): print(items.string[-1])
		items.string.append('Base: {0} [{1}], Upper: {2} [{3}]'.format(
			baseindexvalue, baseindex, upperindexvalue, upperindex))
		if (verbose): print(items.string[-1])
		# items.string.append('Number of items in sublist: {0}'.format(length))
		# if (verbose): print(items.string[-1])

		# statistical function generation starts here
		unique = items.get_unique_content(baseindex, upperindex)
		on_conn, off_conn = cnt_oncampus_requests(unique, oncampaddr, items.string)

		# get total number of unique items per logfile
		if (iter == 1):
			unique_items = len(unique)
			unique_on_conn = on_conn
			unique_off_conn = off_conn
		else:
			unique_items += len(unique)
			unique_on_conn += on_conn
			unique_off_conn += off_conn

		# checks if timeslice is the last one
		# ends loop if timeslice reaches EOL
		if x == timeslices-1: break
		else: basetime = uppertime

	items.finalize()
	common_sites = items.get_unique_sites()	#[0] - site, [1] - frequency
	# print(type(common_sites))
	# for i in common_sites: print (i)
	global_data[1].append(unique_items)
	global_data[2].append(unique_on_conn)
	global_data[3].append(unique_off_conn)
	global_data[4].append(len(common_sites))

	for sites, freq in common_sites:
		global_data[5].append(sites)
		global_data[6].append(freq)

	items.string.append('Total no. of unique items in log: {0}'.format(unique_items))
	print(items.string[-1])

	temp = '\n'.join(i for i in items.string) + '\n'
	ezparse.dump_string_to_out(temp, statfile, mode)
	return items

def cnt_oncampus_requests(data, oncampaddr, strings):
	on_campus_count = 0
	off_campus_count = 0
	unicode_ip_net = str(oncampaddr)
	for i in range(len(data)):
		unicode_ip_request = str(data[i][0])
		if ipaddress.ip_address(
			unicode_ip_request) in ipaddress.ip_network(unicode_ip_net):
			on_campus_count += 1
		else: off_campus_count += 1
	strings.append('Number of on-campus accesses: {0}'.format(on_campus_count))
	if (verbose): print(strings[-1])
	strings.append('Number of off-campus accesses: {0}'.format(off_campus_count))
	if (verbose): print(strings[-1])
	return on_campus_count, off_campus_count

# generate plots for statistical data
# parameters: generate_bar_graph
# (x_axis, item_label, x_items, y_items, x_label, y_label, title, filename)
# paramters: generate_pie_chart
# (sizes, labels, title, filename)
def plot_data(plot, global_data, dir):
	if (plot and dir!=None):
		ezplot.generate_bar_graph(
			np.arange(len(global_data[0])),
			[s.strip(dir+'ezp.') for s in global_data[0]],
			global_data[0], global_data[1], '', 'Total no. of Requests',
			'Total no. of Unique Requests in One Year', 'plot_requests_total.png'
			)
		ezplot.generate_pie_chart(
			[sum(global_data[2]), sum(global_data[3])],
			['On Campus', 'Off Campus'], 'Percentage of Total Connections',
			'plot_connections_total.png'
			)
        # FIXME: Displays all sites (too much for a graph)
        # find a way to display only around the top 5 sites per month
		ezplot.generate_bar_graph(
			np.arange(len(global_data[5])), global_data[5],
			global_data[5], global_data[6], '', 'Frequency',
			'Top Sites per Month', 'plot_sites_frequency.png'
			)
	else: pass