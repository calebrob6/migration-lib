#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.

import os
import csv

import numpy as np

CONTINENTAL_STATE_FIPS = ["01","04","05","06","08","09","10","12","13","16","17","18","19","20","21","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53","54","55","56","22"]

YEAR_FN_MAP = {
    # year : (dirname, infilename, outfilename),
    2004 : ("county0405","countyin0405us1.dat","countyout0405us1.dat"),
    2005 : ("county0506","countyin0506.dat","countyout0506.dat"),
    2006 : ("county0607","countyin0607.dat","countyout0607.dat"),
    2007 : ("county0708","ci0708us.dat","co0708us.dat"),
    2008 : ("county0809","countyinflow0809.csv","countyoutflow0809.csv"),
    2009 : ("county0910","countyinflow0910.csv","countyoutflow0910.csv"),
    2010 : ("county1011","countyinflow1011.csv","countyoutflow1011.csv"),
    2011 : ("county1112","countyinflow1112.csv","countyoutflow1112.csv"),
    2012 : ("county1213","countyinflow1213.csv","countyoutflow1213.csv"),
    2013 : ("county1314","countyinflow1314.csv","countyoutflow1314.csv"),
    2014 : ("county1415","countyinflow1415.csv","countyoutflow1415.csv"),
}

BASE_RAW_DATA_DIR = "/home/caleb/Dropbox/data/migration"

def getRawFnFromYear(year):
    '''
    Input: year - the year of data to get as an int
    Output: inFn, outFn - absolute paths to the inflow and outflow filenames 
    '''
    if year in YEAR_FN_MAP:
        inFn = os.path.join(BASE_RAW_DATA_DIR,YEAR_FN_MAP[year][0],YEAR_FN_MAP[year][1])
        outFn = os.path.join(BASE_RAW_DATA_DIR,YEAR_FN_MAP[year][0],YEAR_FN_MAP[year][2])

        return inFn,outFn
    else:
        raise ValueError("Year %d out of range" % (year))

def getMigrationMatrixRange(startYear,endYear):
    return [getMigrationMatrix(year) for year in range(startYear,endYear)]

def getMigrationMatrix(year, baseDir="output/"):
    if year in YEAR_FN_MAP:
        fn = os.path.join(baseDir,"migrationMatrix_%d.npy" % (year))
        if os.path.exists(fn):
            return np.load(fn)
        else: #Make the file
            outputBase = os.path.dirname(fn)
            if outputBase!='' and not os.path.exists(outputBase):
                os.makedirs(outputBase)

            T = processRawMigrationData(year)
            np.save(fn, T) 
            return T
    else:
        raise ValueError("Year %d out of range" % (year))
 

def processRawMigrationData(year,countyFips=None,verbose=False):
    if countyFips is None:
        countyFips = getCountyList()
    countySet = set(countyFips)
    countyFips_Index = {fips:i for i,fips in enumerate(countyFips)}
    n = len(countyFips)

    migrationMatrix = np.zeros((n,n), dtype=np.int)
    
    inRecords, outRecords = loadFile(year)

    for origin,destination,val in inRecords:
        if 2004<=year<2008: # the 2004 - 2008 data has this backwards
            origin, destination = destination, origin

        if origin in countySet and destination in countySet:
            migrationMatrix[countyFips_Index[origin],countyFips_Index[destination]] = val

    repeats = 0
    numMigrantsDiscrepancy = 0
    for origin,destination,val in outRecords:
        if origin in countySet and destination in countySet:

            if migrationMatrix[countyFips_Index[origin],countyFips_Index[destination]]!=0:
                if migrationMatrix[countyFips_Index[origin],countyFips_Index[destination]]!=val:
                    repeats += 1
                    numMigrantsDiscrepancy += abs(migrationMatrix[countyFips_Index[origin],countyFips_Index[destination]]-val)

            migrationMatrix[countyFips_Index[origin],countyFips_Index[destination]] = val
    
    if verbose:
        print "Found %d repeats" % (repeats)
        print "Error of %d migrants" % (numMigrantsDiscrepancy)

    return migrationMatrix

def parse0408FixedLengthRow(line):
    returnDict = dict()

    returnDict["State_Code_Origin"] = line[0:2].strip()
    returnDict["County_Code_Origin"] = line[3:6].strip()
    returnDict["State_Code_Dest"] = line[7:9].strip()
    returnDict["County_Code_Dest"] = line[10:13].strip()
    returnDict["State_Abbrv"] = line[14:16].strip()
    returnDict["County_Name"] = line[17:49].strip()
    returnDict["Return_Num"] = line[50:59].strip()
    returnDict["Exmpt_Num"] = line[60:70].strip()
    returnDict["Aggr_AGI"] = line[71:82].strip()
    
    return returnDict

def loadFile04_08(fn):

    originSet = set()
    destinationSet = set()

    records = []

    f = open(fn,"r")
    for line in f:
        line = line.strip()
        if line!="":
            row = parse0408FixedLengthRow(line)

            val = int(row["Exmpt_Num"])

            origin = "%02d%03d" % (int(row["State_Code_Origin"]), int(row["County_Code_Origin"]))
            destination = "%02d%03d" % (int(row["State_Code_Dest"]), int(row["County_Code_Dest"]))

            originSet.add(origin)
            destinationSet.add(destination)
            records.append((origin,destination,val))
    f.close()

    return records

def loadFile08_11(fn):

    originSet = set()
    destinationSet = set()

    records = []

    f = open(fn,"r")
    reader = csv.DictReader(f)
    for row in reader:
        val = int(row["Exmpt_Num"])

        origin = "%02d%03d" % (int(row["State_Code_Origin"]), int(row["County_Code_Origin"]))
        destination = "%02d%03d" % (int(row["State_Code_Dest"]), int(row["County_Code_Dest"]))

        originSet.add(origin)
        destinationSet.add(destination)
        records.append((origin,destination,val))
    f.close()

    return records

def loadFile11_15(fn):

    originSet = set()
    destinationSet = set()

    records = []

    f = open(fn,"r")
    reader = csv.DictReader(f)
    for row in reader:
        val = int(row["n2"])

        origin = "%02d%03d" % (int(row["y1_statefips"]), int(row["y1_countyfips"]))
        destination = "%02d%03d" % (int(row["y2_statefips"]), int(row["y2_countyfips"]))

        originSet.add(origin)
        destinationSet.add(destination)
        records.append((origin,destination,val))
    f.close()

    return records

def getCountyList():
    f = open("data/countyIntersection.txt")
    countyFips = map(str,f.read().strip().split("\n"))
    f.close()
    return countyFips


def loadFile(year):
    inFn,outFn = getRawFnFromYear(year)

    inRecords = None
    outRecords = None
    if 2004<=year<2008:
        inRecords = loadFile04_08(inFn)
        outRecords = loadFile04_08(outFn)
    elif 2008<=year<2011: 
        inRecords = loadFile08_11(inFn)
        outRecords = loadFile08_11(outFn)
    elif 2011<=year<2015:
        inRecords = loadFile11_15(inFn)
        outRecords = loadFile11_15(outFn)

    return inRecords, outRecords

def generateMigrationStats():
    import time
    import matplotlib.pyplot as plt
    plt.style.use("seaborn-paper")

    xVals = []
    yVals = []

    f = open("output/migrationStats.csv","w")
    f.write("Year,Number of counties without outgoing migrants,Number of counties without incoming migrants,Number of counties without incoming or outgoing,Total number of migrants\n")
    for year in range(2004,2014+1):
        print "Processing migration matrix for year %d" % (year)
        print "-" * 40
        startTime = float(time.time())
        T = processRawMigrationData(year,verbose=True)

        np.fill_diagonal(T,0)

        rowSums = T.sum(axis=1) 
        colSums = T.sum(axis=0)

        zeroOutgoing = rowSums==0
        zeroIncoming = colSums==0
        zeroBoth = zeroOutgoing & zeroIncoming

        print "Number of counties with no outgoing migrants: \t%d" % zeroOutgoing.sum()
        print "Number of counties with no incoming migrants: \t%d" % zeroIncoming.sum()
        print "Number of counties without any migrations:    \t%d" % zeroBoth.sum()
        print ""
        print "Total number of migrants: %d" % (T.sum())

        f.write("%d,%d,%d,%d,%d\n" % (year, zeroOutgoing.sum(), zeroIncoming.sum(), zeroBoth.sum(), T.sum()))

        xVals.append(year)
        yVals.append(T.sum())

        print "Finished loading and saving raw migration data for %d in %0.4f seconds" % (year, time.time()-startTime)
        print "\n\n"
    f.close()

    # Plot the total number of migrants for each year
    plt.figure(figsize=(6,4))
    plt.plot(xVals,yVals)
    plt.title("Number of migrations over time")
    plt.xlabel("Year")
    plt.ylabel("Number of migrations")
    plt.savefig("output/numberOfMigrationsOverTime.png",dpi=150,bbox_inches='tight',pad_inches=0)
    plt.close()


def getLargestFipsOverlap(startYear,verbose=False):
    
    fipsSets = []

    for year in range(startYear,2015):
        inRecords,outRecords = loadFile(year)

        fipsSet = set()
        for origin,destination,val in inRecords:
            fipsSet.add(origin)
            fipsSet.add(destination)
        for origin,destination,val in outRecords:
            fipsSet.add(origin)
            fipsSet.add(destination)
        if verbose:
            print "%d -- %d counties" % (year, len(fipsSet)) 
        fipsSets.append(fipsSet)

    joinedSet = set(fipsSets[0])
    for s in fipsSets[1:]:
        joinedSet.intersection_update(s)
    
    print "Total of %d locations in common to all years" % (len(joinedSet))

    f = open("output/largestCountyIntersection_%d_2014_allLocations.txt" % (startYear), "w")
    for countyFips in list(joinedSet):
        f.write("%s\n" % (countyFips))
    f.close()

    print "Checking to see how many locations are in the %d CONTINENTAL_STATE_FIPS and not summary codes" % (len(CONTINENTAL_STATE_FIPS))
    filteredJoinedSet = set()
    for countyFips in joinedSet:
        stateCode = countyFips[:2]
        countyCode = countyFips[2:]
        if stateCode in CONTINENTAL_STATE_FIPS and countyCode!="000":
            filteredJoinedSet.add(countyFips)

    f = open("output/largestCountyIntersection_%d_2014_stateLocations.txt" % (startYear), "w")
    filteredJoined = {countyFips:int(countyFips) for countyFips in list(filteredJoinedSet)}
    filteredJoinedList = sorted(filteredJoined, key=filteredJoined.get)
    for countyFips in filteredJoinedList:
        f.write("%s\n" % (countyFips))
    f.close()
    print "Total of %d locations in continental states that are common to all years" % (len(filteredJoinedSet))

if __name__ == "__main__":
    pass