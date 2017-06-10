#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.

import sys
import os
import time
import csv

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
    progName = 'Make sense of country codes'
    print 'Starting %s' % (progName)
    startTime = float(time.time())

    shapefileDataHeader, shapefileData = loadCSV("data/shapefiles/GLOBAL/world2.csv", header=True, DELIM=",", QUOTECHAR='"')
    #print shapefileDataHeader
    shapefileCodeNames = {}
    shapefileCountryCodes = set()
    for row in shapefileData:
        shapefileCountryCodes.add(row[1])
        shapefileCodeNames[row[1]] = row[0]

    f = open("output/global_country_list.txt","r")
    migrationData = f.read().strip().split("\n")
    migrationCodeNames = {}
    migrationCountryCodes = set()
    for row in migrationData:
        countryName = row[:-5].strip()
        countryCode = row[-4:-1].strip()
        migrationCountryCodes.add(countryCode)
        migrationCodeNames[countryCode] = countryName
    f.close()

    featureDataHeader, featureData = loadCSV("data/FEATURES/GLOBAL/worldFeatures_allYears.csv", header=True, DELIM="|", QUOTECHAR='"')
    #print featureDataHeader
    featureCodeNames = {}
    featureCountryCodes = set()
    for row in featureData:
        featureCountryCodes.add(row[1])
        featureCodeNames[row[1]] = row[0]

    #print shapefileCountryCodes 
    #print migrationCountryCodes
    #print featureCountryCodes

    #print len(shapefileCountryCodes)
    #print len(migrationCountryCodes)
    #print len(featureCountryCodes)

    allSets = [shapefileCountryCodes,migrationCountryCodes,featureCountryCodes]
    joinedSet = set(allSets[0])
    for s in allSets[1:]:
        joinedSet.intersection_update(s)
    
    f = open("temp.csv","w")
    for code in joinedSet:
        f.write("%s|%s|%s|%s\n" % (code, shapefileCodeNames[code], migrationCodeNames[code], featureCodeNames[code]))
    f.close()


    print "Shapefile Codes Difference"
    for code in shapefileCountryCodes - joinedSet:
        print code, "\t", shapefileCodeNames[code]

    print "\n\n"

    print "Migration Codes Difference"
    for code in migrationCountryCodes - joinedSet:
        print code, "\t", migrationCodeNames[code]

    print "\n\n"

    print "Feature Codes Difference"
    for code in featureCountryCodes - joinedSet:
        print code, "\t", featureCodeNames[code]



    print len(joinedSet)

    print 'Finished in %0.4f seconds' % (time.time() - startTime)

if __name__ == '__main__':
    #sys.argv = ['programName.py','--input','test.txt','--output','tmp/test.txt']
    main()