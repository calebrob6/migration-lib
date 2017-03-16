#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Methods for interacting with the US American Community Survey 5-year Estimates.
'''
import os
import csv

import numpy as np
import pandas as pd

# List of FIPS codes for the 48 continental US states
CONTINENTAL_STATE_FIPS = ["01","04","05","06","08","09","10","12","13","16","17","18","19","20","21","22","23","24","25","26","27","28","29","30","31","32","33","34","35","36","37","38","39","40","41","42","44","45","46","47","48","49","50","51","53","54","55","56"]
assert len(CONTINENTAL_STATE_FIPS) == 48

YEAR_FN_MAP = {
    # year : (dataFn, dataDictionaryFn),
    2009 : ("acs_comprehensiveReport_data_2009.tsv", "acs_comprehensiveReport_dictionary_2009.dct"),
    2010 : ("acs_comprehensiveReport_data_2010.tsv", "acs_comprehensiveReport_dictionary_2010.dct"),
    2011 : ("acs_comprehensiveReport_data_2011.tsv", "acs_comprehensiveReport_dictionary_2011.dct"),
    2012 : ("acs_comprehensiveReport_data_2012.tsv", "acs_comprehensiveReport_dictionary_2012.dct"),
    2013 : ("acs_comprehensiveReport_data_2013.tsv", "acs_comprehensiveReport_dictionary_2013.dct"),
    2014 : ("acs_comprehensiveReport_data_2014.tsv", "acs_comprehensiveReport_dictionary_2014.dct"),
}

# Base directory of ACS census data
BASE_RAW_DATA_DIR = "data/FEATURES/USA"

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getDataDict(year):
    '''Reads the STATA .dct files that socialexplorer.com provides
    
    Input: year - data dictionary year to parse
    Output columnNameMap - mapping from column names in the TSV to human readable names. e.g. "T004_001" = "Total Population:"
    '''

    if year in YEAR_FN_MAP:
        fn = os.path.join(BASE_RAW_DATA_DIR, YEAR_FN_MAP[year][1])
        if os.path.exists(fn):

            columnNameMap = dict()
            f = open(fn,"r")
            f.readline()
            f.readline()
            csvReader = csv.reader(f, delimiter=' ', quotechar='"')
            for row in csvReader:
                if len(row) == 3:
                    key = row[1]
                    value = row[2]
                    columnNameMap[key] = value
            f.close()

            return columnNameMap
        else:
            raise ValueError("Data from year %d has not been downloaded" % (year))
    else:
        raise ValueError("Year %d out of range." % (year))


#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getFeatureRangeWithCommonFeatures(startYear, endYear, featureList=None, cacheAware=True):
    dataFrames = getFeatureRange(startYear, endYear, cacheAware=cacheAware)

    if featureList is None:
        featureList = getCommonColumnNames(startYear,endYear)

    for i in range(len(dataFrames)):
        dataFrames[i] = dataFrames[i][featureList].copy()

    numColumns = len(dataFrames[0].columns)
    for df in dataFrames:
        assert len(df.columns) == numColumns

    return dataFrames,featureList

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getFeatureRange(startYear, endYear, cacheAware=True):
    return [getFeatures(year, cacheAware=cacheAware) for year in range(startYear,endYear)]


def getFeatures(year, baseDir="output/", cacheAware=True, verbose=False):
    if year in YEAR_FN_MAP:
        fn = os.path.join(baseDir, "usa_features_%d.p" % (year))
        if os.path.exists(fn) and cacheAware:
            featureFrame = pd.read_pickle(fn)
            return featureFrame
        else: #Make the file
            outputBase = os.path.dirname(fn)
            if outputBase!='' and not os.path.exists(outputBase):
                os.makedirs(outputBase)
            featureFrame = processRawACSData(year)
            pd.to_pickle(featureFrame,fn) 
            return featureFrame
    else:
        raise ValueError("Year %d out of range." % (year))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def processRawACSData(year, countyFips=None, verbose=False):
    ''' Parses the raw ACS tab delimited file downloaded from socialexplorer.com

    Returns a pandas DataFrame where columns are the column headers from the datadict (e.g. T105_001), and index is county FIPS codes.
    '''
    if year not in YEAR_FN_MAP:
        raise ValueError("Year %d out of range." % (year))

    fn = os.path.join(BASE_RAW_DATA_DIR, YEAR_FN_MAP[year][0])
    
    if countyFips is None:
        countyFips = getCountyList()
    
    countySet = set(countyFips)
    countyFips_Index = {fips:i for i,fips in enumerate(countyFips)}
    assert len(countySet) == len(countyFips), "List of counties should not have duplicates"
    n = len(countyFips)

    numFeatures = 0
    featureList = []
    dataDict = getDataDict(year)
    for key in dataDict.keys():
        if key.startswith("T") and "_" in key:
            numFeatures += 1
            featureList.append(key)
    featureName_Index = {feature:i for i,feature in enumerate(featureList)}

    featureMatrix = np.zeros((n,numFeatures), dtype=np.float32)

    tempCount = 0
    f = open(fn,"r")
    headerLine = f.readline().strip().split("\t")
    headers = []
    for headerVal in headerLine:
        if "Geo_" in headerVal:
            headers.append(headerVal.split("Geo_")[1])
        elif "SE_" in headerVal:
            headers.append(headerVal.split("SE_")[1])
        else:
            raise ValueError("Column header not expected: %s" % (headerVal))
        
    reader = csv.DictReader(f, fieldnames=headers, delimiter="\t")
    for row in reader:
        fips = row["FIPS"]

        if fips in countySet:

            for featureName in featureList:
                rowIndex = countyFips_Index[fips]
                columnIndex = featureName_Index[featureName]

                if row[featureName] != "":
                    featureMatrix[rowIndex,columnIndex] = float(row[featureName])
                else:
                    featureMatrix[rowIndex,columnIndex] = np.NaN

            tempCount+=1
    f.close()
    assert tempCount == n

    featureFrame = pd.DataFrame(featureMatrix, columns=featureList, index=countyFips)
    return featureFrame

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def dataDictLookup(dd, field):
    '''Returns all the keys for which `field` matches the value'''
    keys = []
    for key, value in dd.items():
        if value==field:
            keys.append(key)
    return keys

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getCommonColumnNames(startYear,endYear):
    dfs = getFeatureRange(startYear,endYear)
    columnSets = [set(df.columns) for df in dfs]
    uniqueSet = columnSets[0]
    for s in columnSets[1:]:
        uniqueSet.intersection_update(s)

    uniqueColumns = list(uniqueSet)
    return uniqueColumns

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getCommonColumnHumanReadableNames(startYear,endYear):
    uniqueColumns = getCommonColumnNames(startYear,endYear)

    dataDictionaries = [getDataDict(year) for year in range(startYear,endYear)]
    mergedDataDictionary = {}

    for columnName in uniqueColumns:
        for dataDict in dataDictionaries:
            columnHumanName = dataDict[columnName]
            if columnName in mergedDataDictionary:
                '''
                if mergedDataDictionary[columnName].lower() != columnHumanName.lower():
                    print "Error have: %s\nWas expecting: %s" % (columnHumanName, mergedDataDictionary[columnName])
                    print "----"
                    break
                '''
                pass
            else:
                mergedDataDictionary[columnName] = columnHumanName
    
    return mergedDataDictionary

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
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

if __name__ == "__main__":
    pass