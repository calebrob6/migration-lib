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

# List of FIPS codes for the 48 continental US states
CONTINENTAL_STATE_FIPS = ["01","04","05","06","08","09","10","12","13","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53","54","55","56"]
assert len(CONTINENTAL_STATE_FIPS) == 48


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

# Base directory of IRS Data
BASE_RAW_DATA_DIR = "data/USA"

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


def getMigrationMatrix(year, baseDir="output/", verbose=False):
    if year in YEAR_FN_MAP:
        fn = os.path.join(baseDir,"usa_migrationMatrix_%d.npy" % (year))
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
    
    # Sanity check, there should not be any u,v in the inRecords that interfere with records from the outRecords
    if verbose:
        print "Found %d repeats" % (repeats)
        print "Error of %d migrants" % (numMigrantsDiscrepancy)

    return migrationMatrix


def parse0408FixedLengthRow(line):
    ''' This method parses rows from the 2004-2008 IRS migration data.
    
    This data is in a fixed width data format where column names are like the following:
    State_Code_Origin, County_Code_Origin, State_Code_Dest, County_Code_Dest, State_Abbrv, County_Name, Return_Num, Exmpt_Num, Aggr_AGI
    '''
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
    ''' Method to load 2004-2008 IRS migration data from file.
    '''
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
    ''' Method to load 2008-2011 IRS migration data from file.
    '''
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
    ''' Method to load 2011-2015 IRS migration data from file.
    '''
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


def getCountyList(fn="output/largestCountyIntersection_2004_2014.txt"):
    '''Loads list of common county FIPS from file. The ordering of this file will be the order of the output migration matrices.
    '''
    if not os.path.isfile(fn):
        raise IOError("File `%s` does not exist. Try running `calculateCommonCounties.py` first." % (fn))

    f = open(fn)
    lines = f.read().strip().split("\n")
    f.close()

    countyFips = []
    for line in lines:
        line = line.strip()
        if line!="":
            countyFips.append(line)

    return countyFips


def loadFile(year):
    ''' Wrapper method around the individual methods to load migration data from file. Takes as input an year as integer, returns a list of records from the data.
    '''
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


if __name__ == "__main__":
    import time
    print "Generating output migration matrices in ./output/"
    startTime = float(time.time())

    for year in range(2004,2014+1):
        T = getMigrationMatrix(year, baseDir="./output/", verbose=True)

    print "Finished generating output matrices in %0.4f seconds" % (time.time() - startTime)