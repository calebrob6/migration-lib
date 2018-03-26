#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Usage: python splitGlobalFeatures.py

This file splits the World Bank World Development Indicators data into yearly chunks.
'''

import sys
import os
import time
import csv
import argparse

def loadCSV(fn, header=False, DELIM='|', QUOTECHAR=None):
    f = open(fn,'rb')
    csvReader = csv.reader(f, delimiter=DELIM, quotechar=QUOTECHAR)

    if header:
        headerLine = csvReader.next()

    data = []
    for row in csvReader:
        data.append(row)

    f.close()

    if header:
        return headerLine, data
    else:
        return data

#---------------------------------------------------------------------------------------------------
def main():
    print('Starting global feature data parser')
    startTime = float(time.time())

    # this csv file contains a row for each (country, feature) pair, and a column for each year of data
    # we want each year of data to be in a separate file
    header, data = loadCSV("data/FEATURES/GLOBAL/worldFeatures.csv", header=True, DELIM='|')

    dataSplit = 4 #this is the index of the first column of data

    # here we convert column names in the form "1960 [YR1960]" to "1960"
    years = []
    for i in range(dataSplit,len(header)):
        parts = header[i].split(" ")
        years.append(parts[0])

    # dataYears has one key for each year of data, the values are a list of rows that go with that year
    dataYears = {year:[] for year in years}
    for row in data:
        baseRow = row[:dataSplit]
        for i,val in enumerate(row[dataSplit:]):
            newRow = list(baseRow) + [val] 
            dataYears[years[i]].append(newRow)
    
    # writing the data to file
    for year,rows in dataYears.items():
        print("Writing file for %s" % (year))
        f = open("data/FEATURES/GLOBAL/global_features_%s.csv" % (year), "w")
        f.write("%s|%s\n" % ('|'.join(header[:dataSplit]), year))
        for row in rows:
            f.write("%s\n" % ('|'.join(row)))
        f.close()
   
    print('Finished in %0.4f seconds' % (time.time() - startTime))

if __name__ == '__main__':
    print(__doc__)
    print("")
    main()