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

YEAR_FN_MAP = {
    # year : filename
    1960 : "migrations_1960.csv",
    1970 : "migrations_1970.csv",
    1980 : "migrations_1980.csv",
    1990 : "migrations_1990.csv",
    2000 : "migrations_2000.csv"
}

# Base directory of World Bank Global Bilateral Migration data
BASE_RAW_DATA_DIR = "data/MIGRATION/GLOBAL"


def getRawFnFromYear(year):
    '''
    Input: year - the year of data to get as an int
    Output: fn - absolute paths to the raw data filename
    '''
    if year in YEAR_FN_MAP:
        fn = os.path.join(BASE_RAW_DATA_DIR,YEAR_FN_MAP[year])

        return fn
    else:
        raise ValueError("Year %d out of range" % (year))


def getMigrationMatrixRange(startYear,endYear,step=10):
    return [getMigrationMatrix(year) for year in range(startYear,endYear,step)]


def getMigrationMatrix(year, baseDir="output/", cacheAware=True, verbose=False):
    if year in YEAR_FN_MAP:
        fn = os.path.join(baseDir,"global_migrationMatrix_%d.npy" % (year))
        if os.path.exists(fn) and cacheAware:
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


def processRawMigrationData(year,countryCodes=None,verbose=False):
    
    if countryCodes is None:
        countryCodes = getCountryList()

    countrySet = set(countryCodes)
    countryCodes_Index = {code:i for i,code in enumerate(countryCodes)}
    assert len(countrySet) == len(countryCodes), "List of countries should not have duplicates"
    n = len(countryCodes)

    migrationMatrix = np.zeros((n,n), dtype=np.int)
    
    records = loadFile(year)

    repeats = 0
    for origin,destination,val in records:
        if origin in countrySet and destination in countrySet:

            if migrationMatrix[countryCodes_Index[origin],countryCodes_Index[destination]]!=0:
                if migrationMatrix[countryCodes_Index[origin],countryCodes_Index[destination]]!=val:
                    repeats += 1
            
            migrationMatrix[countryCodes_Index[origin],countryCodes_Index[destination]] = val
    
    # Sanity check, there should not be any u,v in the inRecords that interfere with records from the outRecords
    if verbose:
        print "Found %d repeats" % (repeats)

    return migrationMatrix


def loadGlobalBilateralMigration(fn):
    ''' Method to load World Bank Global migration data from file.
    '''
    records = []

    f = open(fn,"r")
    headerLine = f.readline().strip().split("|")
    reader = csv.reader(f, delimiter="|")
    for row in reader:
        assert len(row) == len(headerLine)

        origin = "%s [%s]" % (row[4], row[5])

        for j in range(6,len(row)):
            destination = headerLine[j]

            val = None
            if row[j] == "..":
                val = 0
            else:
                val = int(row[j])

            if val!=0:
                records.append((origin,destination,val))
    f.close()

    return records


def getCountryList(fn="output/global_country_list.txt"):
    '''Loads list of common country codes from file. The ordering of this file will be the order of the output migration matrices.
    '''
    if not os.path.isfile(fn):
        raise IOError("File `%s` does not exist. Try running `calculateCommonCountries.py` first." % (fn))

    f = open(fn)
    lines = f.read().strip().split("\n")
    f.close()

    countryCodes = []
    for line in lines:
        line = line.strip()
        if line!="":
            countryCodes.append(line)

    return countryCodes


def loadFile(year):
    ''' Wrapper method around the individual methods to load migration data from file. Takes as input an year as integer, returns a list of records from the data.
    '''
    fn = getRawFnFromYear(year) # will throw error if year isn't allowed

    records = loadGlobalBilateralMigration(fn)

    return records


if __name__ == "__main__":
    import time
    print "Generating output migration matrices in ./output/"
    startTime = float(time.time())

    for year in range(1960,2000+10,10):
        T = getMigrationMatrix(year, baseDir="./output/", verbose=True)
        print year, T.sum()

    print "Finished generating output matrices in %0.4f seconds" % (time.time() - startTime)