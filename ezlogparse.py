#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:18:35 2018

@authors:
Norman Roy de Guia
Al Tristan Bandiola
"""
import sys;

def main(filename):
    #filename = "sample_data"
    print("filename is:", filename);
    
    # Open data file and store in data vector.
    data = open(filename, 'r');
    data.seek(0);
    data_count = len(data.readlines());
    data.seek(0);
    print(data.read());
    print("Total lines in dataset is", data_count);
    data.seek(0);
    
    data_arr = list(data);
    data_arr = [i.split(' ') for i in data_arr];
    
    data.close();
    
    # find lookup string and isolate
    lookup = '.pdf';
    final_arr = [];
    for i in range(data_count):
        if lookup in data_arr[i][6]:
            final_arr.append(data_arr[i]);
            
    ip = [];
    name = [];
    date = [];
    tzone = [];
    request = [];
    final_arr_count = len(final_arr);
    
    # parse and store needed data
    for x in range(final_arr_count):
        ip.append(final_arr[x][0]);
        name.append(final_arr[x][2]);
        date.append(final_arr[x][3].strip("["));
        tzone.append(final_arr[x][4].strip("]"));
        request.append(final_arr[x][6]);

if __name__ == "__main__": #main();
    main(sys.argv[1]);
