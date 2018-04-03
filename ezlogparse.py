#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 16:18:35 2018

@author: norman
"""
#import sys;

#def main():
filename = "sample_data"
print("filename is:", filename);

# Open data file and store in data vector.
data = open(filename, 'r');
data.seek(0);
data_count = len(data.readlines());
data.seek(0);
print(data.read());
print("Total lines in dataset is", data_count);
data.seek(0);

data_arr = [0 for x in range(data_count)];
for x in range(data_count):
    data_arr[x] = (data.readline()).split(" ");

data.close();

lookup = ".pdf";
final_arr = [];
for i in range(data_count):
    if lookup in data_arr[i][6]:
        final_arr.append(data_arr[i]);
        
ip_arr = [];
final_arr_count = len(final_arr);
split_count = 10;
for x in range(final_arr_count):
    print("count");
    ip_arr.append(final_arr[x][0]);

#if __name__ == "__main__": main();
    #main(sys.argv[1]);