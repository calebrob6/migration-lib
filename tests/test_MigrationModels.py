import sys
import os
import unittest

import numpy as np

sys.path.append(os.path.dirname(".."))

import MigrationModels

#-----------------------------------------------------------------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------------------------------------------------------------
EPSILON = 0.000001

def getToyDistanceMatrix(n):
    D = np.random.randint(1,n**2,size=(n,n))
    D+=D.T  
    np.fill_diagonal(D,0)
    return D

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class InterveningOpportunitiesTests(unittest.TestCase):

    def testCorrectness(self):
        for i in range(10):
            n = 100
            distanceMatrix = getToyDistanceMatrix(n)
            features = np.random.randint(1,5,size=(n,1))
            
            i1 = MigrationModels.getInterveningOpportunities(features,distanceMatrix)
            i2 = MigrationModels.getInterveningOpportunities(features,distanceMatrix,slowMode=True)

            self.assertTrue(np.all(np.abs(i1-i2) < EPSILON))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class ExtendedRadiationModelTests(unittest.TestCase):

    def testCorrectnessNormalize(self):
        n = 100
        distanceMatrix = getToyDistanceMatrix(n)
        features = np.random.randint(1,5,size=(n,1))
        s = MigrationModels.getInterveningOpportunities(features,distanceMatrix)

        p1 = MigrationModels.extendedRadiationModel(features, features, s, 1.5, rowNormalize=True)
        p2 = MigrationModels.extendedRadiationModel(features, features, s, 1.5, rowNormalize=True, slowMode=True)

        self.assertTrue(np.all(np.abs(p1-p2) < EPSILON))
        self.assertTrue(np.all(np.abs(p1.sum(axis=1)-1.0) < EPSILON )) # all rows should sum to 1 (this might not be the case if any of the features are `0`)
    
    def testCorrectnessNoNormalize(self):
        n = 100
        distanceMatrix = getToyDistanceMatrix(n)
        features = np.random.randint(1,5,size=(n,1))
        s = MigrationModels.getInterveningOpportunities(features,distanceMatrix)

        p1 = MigrationModels.extendedRadiationModel(features, features, s, 1.5, rowNormalize=False)
        p2 = MigrationModels.extendedRadiationModel(features, features, s, 1.5, rowNormalize=False, slowMode=True)

        self.assertTrue(np.all(np.abs(p1-p2) < EPSILON))

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class RadiationModelTests(unittest.TestCase):

    def testCorrectnessNormalize(self):
        n = 100
        distanceMatrix = getToyDistanceMatrix(n)
        features = np.random.randint(1,5,size=(n,1))
        s = MigrationModels.getInterveningOpportunities(features,distanceMatrix)

        p1 = MigrationModels.radiationModel(features, features, s, rowNormalize=True)
        p2 = MigrationModels.radiationModel(features, features, s, rowNormalize=True, slowMode=True)

        self.assertTrue(np.all(np.abs(p1-p2) < EPSILON))
        self.assertTrue(np.all(np.abs(p1.sum(axis=1)-1.0) < EPSILON )) # all rows should sum to 1 (this might not be the case if any of the features are `0`)

#-----------------------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------------------
class GravityModelTests(unittest.TestCase):

    def testCorrectnessPowerLaw(self):
        n = 100
        distanceMatrix = getToyDistanceMatrix(n)
        features = np.random.randint(1,5,size=(n,1))

        p1 = MigrationModels.gravityModel(features, features, distanceMatrix, 1.2, decay="power", rowNormalize=True)
        p2 = MigrationModels.gravityModel(features, features, distanceMatrix, 1.2, decay="power", rowNormalize=True, slowMode=True)

        self.assertTrue(np.all(np.abs(p1-p2) < EPSILON))
        self.assertTrue(np.all(np.abs(p1.sum(axis=1)-1.0) < EPSILON )) # all rows should sum to 1 (this might not be the case if any of the features are `0`)

    def testCorrectnessExponentialLaw(self):
        n = 100
        distanceMatrix = getToyDistanceMatrix(n)
        features = np.random.randint(1,5,size=(n,1))

        p1 = MigrationModels.gravityModel(features, features, distanceMatrix, 0.01, decay="exponential", rowNormalize=True)
        p2 = MigrationModels.gravityModel(features, features, distanceMatrix, 0.01, decay="exponential", rowNormalize=True, slowMode=True)

        self.assertTrue(np.all(np.abs(p1-p2) < EPSILON))
        self.assertTrue(np.all(np.abs(p1.sum(axis=1)-1.0) < EPSILON )) # all rows should sum to 1 (this might not be the case if any of the features are `0`)


if __name__ == '__main__':
    unittest.main()