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

import matplotlib.pyplot as plt; plt.rcdefaults()
import matplotlib.pyplot as plt
import os

# if OS is windows, save plot only (fork doesn't work)
# or good if you can make multithreading work for windows
if (os.name == 'nt'): plt_mode = 'show'
else: plt_mode = 'show'

# this only plots the global unique items per log file
def generate_bar_graph(pos_x_axis, x_item_label, x_items, y_items,
	x_label, y_label, title, filename, rot_value):

	plt.bar(pos_x_axis, y_items, align='center', alpha=0.5)
	plt.xticks(pos_x_axis, x_item_label, rotation=rot_value)
	plt.ylabel(y_label)
	plt.xlabel(x_label)
	plt.title(title)

	genplot(title, filename)

# this only shows the global total connections in all files
def generate_pie_chart(sizes, labels, title, filename):
	colors = ['lightsteelblue', 'cornflowerblue']
	explode = (0.05, 0)
	plt.pie(sizes, explode=explode, labels=labels, colors=colors,
		autopct='%1.1f%%', shadow=False, startangle=140)
	plt.axis('equal')
	plt.title(title)

	genplot(title, filename)

def generate_line_graph(x_items, y_items, x_label, y_label, title, filename):
	plt.plot(x_items, y_items)
	plt.xlabel(x_label)
	plt.ylabel(y_label)

	genplot(title,filename)

def genplot(title, filename):
	if (plt_mode == 'show'):
		print('Display: {0}'.format(title))
		plt.show()
	if (plt_mode == 'save_only'):
		plt.savefig(filename, format='png', dpi=400, bbox_inches='tight')
		print('Saved: {0} as {1}...'.format(title, filename))