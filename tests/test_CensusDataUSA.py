import sys
import os
import unittest

import numpy as np

sys.path.append(os.path.dirname(".."))

import CensusDataUSA

#-----------------------------------------------------------------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------------------------------------------------------------
EPSILON = 0.000001

dataYearMin = min(CensusDataUSA.YEAR_FN_MAP.keys())
dataYearMax = max(CensusDataUSA.YEAR_FN_MAP.keys())

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class DataExistsTest(unittest.TestCase):

    def testIfDataExists(self):
        for year, (dataFn, dataDictFn) in CensusDataUSA.YEAR_FN_MAP.items():
            self.assertTrue(os.path.exists(os.path.join(CensusDataUSA.BASE_RAW_DATA_DIR, dataFn)))
            self.assertTrue(os.path.exists(os.path.join(CensusDataUSA.BASE_RAW_DATA_DIR, dataDictFn)))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class DataDictionaryTests(unittest.TestCase):

    def testLoadDict(self):

        for year in range(dataYearMin, dataYearMax+1):
            dataDict = CensusDataUSA.getDataDict(year)

            self.assertTrue(dataDict is not None)

    def testCommonColumnNames(self):

        commonColumnNames = CensusDataUSA.getCommonColumnNames(dataYearMin, dataYearMax+1)

        for year in range(dataYearMin, dataYearMax+1):
            dataDict = CensusDataUSA.getDataDict(year) 

            self.assertTrue(len(dataDict)>=len(commonColumnNames))

    def testCommonColumnHumanReadableNames(self):

        commonColumnNames = CensusDataUSA.getCommonColumnNames(dataYearMin, dataYearMax+1)
        commonColumnHumanReadableNames = CensusDataUSA.getCommonColumnHumanReadableNames(dataYearMin, dataYearMax+1)

        self.assertTrue(len(commonColumnNames) == len(commonColumnHumanReadableNames))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class DataLoadingTests(unittest.TestCase):

    def testLoadRawData(self):

        for year in range(dataYearMin, dataYearMax+1):
            dataFrame = CensusDataUSA.processRawACSData(year)
            self.assertTrue(len(dataFrame.index) == 3106)

    def testLoadData(self):

        for year in range(dataYearMin, dataYearMax+1):
            dataFrame = CensusDataUSA.getFeatures(year,cacheAware=False)
            self.assertTrue(len(dataFrame.index) == 3106)

    def testLoadDataRange(self):

        dataFrames = CensusDataUSA.getFeatureRange(dataYearMin, dataYearMax+1, cacheAware=False)
        for dataFrame in dataFrames:
            self.assertTrue(len(dataFrame.index) == 3106)

    def testLoadDataRangeWithCommonFeatures(self):

        dataFrames, featureList = CensusDataUSA.getFeatureRangeWithCommonFeatures(dataYearMin, dataYearMax+1, cacheAware=False)

        numFeatures = len(featureList)
        for dataFrame in dataFrames:
            self.assertTrue(len(dataFrame.columns) == numFeatures)

if __name__ == '__main__':
    unittest.main()