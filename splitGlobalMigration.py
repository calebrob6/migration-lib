#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Usage: python splitGlobalMigration.py

This file splits the World Bank Global Bilateral Migration Database data into yearly chunks.
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
    print 'Starting global migration data parser'
    startTime = float(time.time())

    header, data = loadCSV("data/GLOBAL/migrationData.csv", header=True, DELIM='|')
    #print header

    dataYears = dict()
    for row in data:
        year = row[0]
        if year not in dataYears:
            dataYears[year] = []
        dataYears[year].append(row)
    
    for year,rows in dataYears.items():
        print "Writing file for %s" % (year)
        f = open("data/GLOBAL/migrations_%s.csv" % (year), "w")
        f.write("%s\n" % ('|'.join(header)))
        for row in rows:
            f.write("%s\n" % ('|'.join(row)))
        f.close()
   
    print 'Finished in %0.4f seconds' % (time.time() - startTime)

if __name__ == '__main__':
    print __doc__
    print ""
    main()