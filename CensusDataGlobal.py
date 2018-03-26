#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Methods for interacting with the World Bank World Development Indicators (WDI) data
'''
import os
import csv

import numpy as np
import pandas as pd


YEAR_FN_MAP = {
    # year : (dataFn, dataDictionaryFn),
    1960 : ("global_features_1960.csv", "worldFeatures_dictionary.csv"),
    1970 : ("global_features_1970.csv", "worldFeatures_dictionary.csv"),
    1980 : ("global_features_1980.csv", "worldFeatures_dictionary.csv"),
    1990 : ("global_features_1990.csv", "worldFeatures_dictionary.csv"),
    2000 : ("global_features_2000.csv", "worldFeatures_dictionary.csv"),
}

# Base directory of ACS census data
BASE_RAW_DATA_DIR = "data/FEATURES/GLOBAL"

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getDataDict(year):
    '''Reads the dictionary file that goes with the World Development Indicators data 
    
    Note, for the WDI data, the data dictionary is the same over all years.

    Input: year - data dictionary year to parse
    Output columnNameMap - mapping from indicator codes to human readable long names. e.g. "EG.ELC.ACCS.ZS" = "Access to electricity (% of population)"
    '''

    if year in YEAR_FN_MAP:
        fn = os.path.join(BASE_RAW_DATA_DIR, YEAR_FN_MAP[year][1])
        if os.path.exists(fn):

            columnNameMap = dict()
            f = open(fn,"r")
            f.readline()
            csvReader = csv.reader(f, delimiter='|', quotechar='"')
            for row in csvReader:
                key = row[0]
                value = row[1]
                columnNameMap[key] = value
            f.close()

            return columnNameMap
        else:
            raise ValueError("Data from year %d has not been downloaded" % (year))
    else:
        raise ValueError("Year %d out of range." % (year))


#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getFeatureRangeWithCommonFeatures(startYear, endYear, step=10, featureList=None, cacheAware=True):
    dataFrames = getFeatureRange(startYear, endYear, step=step, cacheAware=cacheAware)

    if featureList is None:
        featureList = getCommonColumnNames(startYear,endYear,step)

    for i in range(len(dataFrames)):
        dataFrames[i] = dataFrames[i][featureList].copy()

    numColumns = len(dataFrames[0].columns)
    for df in dataFrames:
        assert len(df.columns) == numColumns

    return dataFrames,featureList

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getFeatureRange(startYear, endYear, step=10, cacheAware=True):
    return [getFeatures(year, cacheAware=cacheAware) for year in range(startYear,endYear,step)]


def getFeatures(year, baseDir="output/", cacheAware=True, verbose=False):
    if year in YEAR_FN_MAP:
        fn = os.path.join(baseDir, "global_features_%d.p" % (year))
        if os.path.exists(fn) and cacheAware:
            featureFrame = pd.read_pickle(fn)
            return featureFrame
        else: #Make the file
            outputBase = os.path.dirname(fn)
            if outputBase!='' and not os.path.exists(outputBase):
                os.makedirs(outputBase)
            featureFrame = processRawWDIData(year)
            pd.to_pickle(featureFrame,fn) 
            return featureFrame
    else:
        raise ValueError("Year %d out of range." % (year))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def processRawWDIData(year, countryCodes=None, verbose=False):
    ''' Parses the raw WDI tab delimited file downloaded from socialexplorer.com

    Returns a pandas DataFrame where columns are the column headers from the datadict (e.g. EG.ELC.ACCS.ZS), and index is the 3 letter country codes.
    '''
    if year not in YEAR_FN_MAP:
        raise ValueError("Year %d out of range." % (year))

    fn = os.path.join(BASE_RAW_DATA_DIR, YEAR_FN_MAP[year][0])
    
    if countryCodes is None:
        countryCodes = getCountryList()
    
    countrySet = set(countryCodes)
    countryCodes_Index = {code:i for i,code in enumerate(countryCodes)}
    assert len(countrySet) == len(countryCodes), "List of countries should not have duplicates"
    n = len(countryCodes)

    numFeatures = 0
    featureList = []
    dataDict = getDataDict(year)
    for key in dataDict.keys():
        numFeatures += 1
        featureList.append(key)
    featureName_Index = {feature:i for i,feature in enumerate(featureList)}

    featureMatrix = np.zeros((n,numFeatures), dtype=np.float32)

    f = open(fn,"r")
    headerLine = f.readline().strip().split("|")
    recognizedCodes = set()
    notRecognizedCodes = set()
    reader = csv.reader(f, delimiter="|")
    for row in reader:
        Country_Name, Country_Code, Series_Name, Series_Code, dataVal = row

        countryCode = "%s" % (Country_Code)

        if countryCode in countrySet:
            val = None
            if dataVal=="..":
                val = None
            else:
                val = float(dataVal)
            featureMatrix[countryCodes_Index[countryCode], featureName_Index[Series_Code]] = val
            recognizedCodes.add(countryCode)
        else:
            notRecognizedCodes.add(countryCode)
    f.close()

    print(countrySet - recognizedCodes)
    assert len(countrySet) - len(recognizedCodes) == 0

    featureFrame = pd.DataFrame(featureMatrix, columns=featureList, index=countryCodes)
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
def getCommonColumnNames(startYear, endYear, step=10):
    dfs = getFeatureRange(startYear,endYear,step=step)
    columnSets = [set(df.columns) for df in dfs]
    uniqueSet = columnSets[0]
    for s in columnSets[1:]:
        uniqueSet.intersection_update(s)

    uniqueColumns = list(uniqueSet)
    return uniqueColumns

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
def getCommonColumnHumanReadableNames(startYear, endYear, step=10):
    uniqueColumns = getCommonColumnNames(startYear,endYear,step)

    dataDictionaries = [getDataDict(year) for year in range(startYear,endYear,step)]
    mergedDataDictionary = {}

    for columnName in uniqueColumns:
        for dataDict in dataDictionaries:
            columnHumanName = dataDict[columnName]
            if columnName in mergedDataDictionary:
                pass
            else:
                mergedDataDictionary[columnName] = columnHumanName
    
    return mergedDataDictionary

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
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

if __name__ == "__main__":
    
    dataFrames, featureList = getFeatureRangeWithCommonFeatures(1970,2001)
    humanReadable = getCommonColumnHumanReadableNames(1970,2001)
    

    featureMap = {featureCode : 1.0 for featureCode in featureList}
    for df in dataFrames:
        nullVals = np.isnan(df.as_matrix())
        percentNulls = nullVals.sum(axis=0) / 203.0
        for i, percentVal in enumerate(percentNulls):
            featureMap[featureList[i]] = min(featureMap[featureList[i]], percentVal)


    sortedFeatures = sorted(featureMap, key=featureMap.get)
    for i in range(20):
        print(i, featureMap[sortedFeatures[i]], humanReadable[sortedFeatures[i]], sortedFeatures[i])
