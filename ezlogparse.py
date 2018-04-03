#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:18:35 2018

@authors:
    Norman Roy de Guia
    Al Tristan Bandiola
"""
import sys;

def main(filename, csvfile):
    #filename = "sample_data";
    #csvfile = "parsed_data.csv";
    print("Filename is:", filename);
    
    # Open data file and store in data vector.
    data = open(filename, 'r');
    data.seek(0);
    data_count = len(data.readlines());
    data.seek(0);
    print("Total lines in dataset is", data_count);
    data.seek(0);
    
    data_arr = list(data);
    data_arr = [i.split(' ') for i in data_arr];
    
    data.close(); # close file
    
    # find lookup string and isolate
    lookup = '.pdf';
    parse_arr = [];
    for x in range(data_count):
        if lookup in data_arr[x][6]:
            parse_arr.append(data_arr[x]);
            
    ipaddr = [];
    name = [];
    date = [];
    tzone = [];
    request = [];
    parse_arr_count = len(parse_arr);
    print("Total valuable lines:", parse_arr_count);
    
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
        
    # dump contents to csv file
    csvdump = open(csvfile, "w");
    csvdumpstr = ''.join(final_arr);
    csvdump.write(csvdumpstr);

if __name__ == "__main__": #main();
    main(sys.argv[1], sys.argv[2]);
