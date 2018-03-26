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
    print('Starting %s' % (progName))
    startTime = float(time.time())


    f = open("output/global_country_list.txt","r")
    migrationData = f.read().strip().split("\n")
    migrationCodeNames = {}
    migrationCountryCodes = set()
    for row in migrationData:
        parts = row.split("|")
        countryName = parts[0]
        countryCode = parts[1]
        migrationCountryCodes.add(countryCode)
        migrationCodeNames[countryCode] = countryName
    f.close()

    featureDataHeader, featureData = loadCSV("data/FEATURES/GLOBAL/worldFeatures_allYears.csv", header=True, DELIM="|", QUOTECHAR='"')
    featureCodeNames = {}
    featureCountryCodes = set()
    for row in featureData:
        featureCountryCodes.add(row[1])
        featureCodeNames[row[1]] = row[0]

    #print(shapefileCountryCodes)
    #print(migrationCountryCodes)
    #print(featureCountryCodes)

    #print(len(shapefileCountryCodes))
    #print(len(migrationCountryCodes))
    #print(len(featureCountryCodes))

    allSets = [migrationCountryCodes,featureCountryCodes]
    joinedSet = set(allSets[0])
    for s in allSets[1:]:
        joinedSet.intersection_update(s)
    
    f = open("temp.csv","w")
    for code in sorted(list(joinedSet)):
        f.write("%s|%s\n" % (migrationCodeNames[code], code))
    f.close()


    print("Migration Codes Difference")
    for code in migrationCountryCodes - joinedSet:
        print(code, "\t", migrationCodeNames[code])

    print("\n\n")

    print("Feature Codes Difference")
    for code in featureCountryCodes - joinedSet:
        print(code, "\t", featureCodeNames[code])

    print(len(joinedSet))

    print('Finished in %0.4f seconds' % (time.time() - startTime))

if __name__ == '__main__':
    #sys.argv = ['programName.py','--input','test.txt','--output','tmp/test.txt']
    main()