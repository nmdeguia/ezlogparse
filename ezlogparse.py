#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:18:35 2018

@authors:
    Norman Roy de Guia
    Al Tristan Bandiola
"""
from collections import Counter
import sys;

def main(filename, csvfile):
    #filename = "sample_data";
    #csvfile = "parsed_data.csv";
    print("Parsing %s." % filename);
    
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

    # generate statistical report on data
    get_statistics(parsed_data);

def parse_data(data, datalen):
    # find lookup string and isolate
    lookup = '.pdf';
    parse_arr = [];
    for x in range(datalen):
        if lookup in data[x][6]:
            parse_arr.append(data[x]);
            
    ipaddr = [];
    name = [];
    date = [];
    tzone = [];
    request = [];
    parse_arr_count = len(parse_arr);
    print("Total valuable lines: %d" % parse_arr_count);
    
    final_arr = [0 for x in range(parse_arr_count)];
    
    # parse and store needed data
    for x in range(parse_arr_count):
        temp = "";
        ipaddr.append(parse_arr[x][0]);
        name.append(parse_arr[x][2]);
        date.append(parse_arr[x][3].strip("["));
        tzone.append(parse_arr[x][4].strip("]"));
        request.append(parse_arr[x][6]);
        temp += ipaddr[x] + ", ";
        temp += name[x] + ", ";
        temp += date[x] + ", ";
        temp += tzone[x] + ", ";
        temp += request[x] + "\n";
        final_arr[x] = temp;

    return final_arr;

def get_statistics(data):
    datalen = len(data);

    print("----------------------------------------");
    print("Statistical Report for acquired dataset:");

    unique_data = Counter(data);
    n_unq_data = len(unique_data);
    print("Number of unique items: %d" % n_unq_data);


if __name__ == "__main__": #main();
    main(sys.argv[1], sys.argv[2]);