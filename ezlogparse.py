#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:18:35 2018

@authors:
    Norman Roy de Guia
    Al Tristan Bandiola
"""
import sys;
from collections import Counter;

ipaddr = [];
name = [];
date = [];
taccess = [];
tzone = [];
request = [];

# debug string for debugging purposes
debug = "debug string";

# in minutes
timewindow = 1440/24/60;

def main(filename, csvfile):
    #filename = "sample_data";
    #csvfile = "parsed_data.csv";
    print("Parsing %s..." % filename);
    
    # Open data file and store in data vector.
    data = open(filename, 'r');
    data.seek(0);
    data_count = len(data.readlines());
    data.seek(0);
    print("Total lines in dataset is  %d." % data_count);
    data.seek(0);
    
    data_arr = list(data);
    data_arr = [i.split(' ') for i in data_arr];
    
    data.close(); # close file
    
    # parse data and store to parsed_data
    parsed_data = parse_data(data_arr, data_count);

    # dump contents to csv file
    csvdump = open(csvfile, "w");
    csvdumpstr = ''.join(parsed_data);
    csvdump.write(csvdumpstr);
    print("Parsing complete, output dump: %s." % csvfile);

    # parse date into more meaningful data
    parse_date();

    # generate statistical report on data
    get_statistics(csvdumpstr);

def parse_data(data, datalen):
    # find lookup string and isolate
    lookup = '.pdf';
    parse_arr = [];
    for x in range(datalen):
        if lookup in data[x][6]:
            parse_arr.append(data[x]);
            
    parse_arr_count = len(parse_arr);
    print("Total valuable lines: %d" % parse_arr_count);
    
    final_arr = [0 for x in range(parse_arr_count)];
    
    # parse and store needed data
    for x in range(parse_arr_count):
        temp = "";
        ipaddr.append(parse_arr[x][0]);
        name.append(parse_arr[x][2]);
        taccess.append(parse_arr[x][3].strip("["));
        tzone.append(parse_arr[x][4].strip("]"));
        request.append(parse_arr[x][6]);
        temp += ipaddr[x] + ", ";
        temp += name[x] + ", ";
        temp += taccess[x] + ", ";
        temp += tzone[x] + ", ";
        temp += request[x] + "\n";
        final_arr[x] = temp;

    return final_arr;

def get_statistics(data):
    print("----------------------------------------");
    print("Statistical Report for acquired dataset:");
    temp = [];
    temp = data.split("\n")[:-1]

    print("Total valuable items: %d " % len(temp));
    items = [0 for x in range(len(temp))];
    for x in range(len(temp)):
        items[x] = temp[x].split(", ");

    get_items_per_timewindow(items);

def get_items_per_timewindow(items):
    print("Time Slice of %d minutes." % (timewindow*24*60));
    print("%d items to slice." % len(items));
    print("%d individual time records." % len(date));

    # compare date here:
    unique_time_slices = 1;
    unique_tslice_index = [0];
    for x in range(len(items)):
        if x + 1 == len(items):
            break;
        # check if year is same as next item    
        if date[x][2] == date[x+1][2]: 
            if date[x][1] == date[x+1][1]:
                # only works for 1 day time slice
                # change code if timewindow < 1 day is needed
                if date[x][0] == date[x+1][0]:
                    pass;
                else:
                    # increment counter of unique slices
                    unique_time_slices += 1;
                    # get starting index of time slice window
                    unique_tslice_index.append(x+1);

    print("%d unique time slices." % unique_time_slices)
    print("Indices of unique time slices: %s" % unique_tslice_index)
    
    # we now have indices of time slices
    # locate index and iterate up to next index - 1
    # count number of same request occurences

def parse_date():
    temp = [];
    # print(isinstance(date, list));
    for x in range(len(taccess)):
        temp = taccess[x][:11].split('/');
        temp += taccess[x][12:].split(':');
        date.append(temp);

if __name__ == "__main__": #main();
    main(sys.argv[1], sys.argv[2]);
