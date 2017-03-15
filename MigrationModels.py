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

import numpy as np
import scipy.spatial
import haversine

def productionFunction(population, P, beta=0.03):
    return P * (population*beta)

def getDistanceMatrix(fn="output/distanceMatrix.npy"):
    if os.path.exists(fn):

        distanceMatrix = np.load(fn)
        assert len(distanceMatrix.shape)==2
        assert distanceMatrix.shape[0] == distanceMatrix.shape[1]

        return distanceMatrix
    else:
        raise ValueError("Distance matrix file doesn't exist")

def extendedRadiationModel(origins, destinations, s, alpha, normalize=True, slowMode=False):
    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert origins.shape[0] == destinations.shape[0], "`origins` and `destinations` must be the same shape"

    n = origins.shape[0]

    assert len(s.shape) == 2 and s.shape[0] == n and s.shape[1] == n, "`s` must be a square matrix with same length/width as the origin and destination features"

    origins = origins.astype(np.float32)
    P = np.zeros((n,n), dtype=float)

    if slowMode:
        for i in range(n):
            for j in range(n):
                numerator = ((origins[i] + destinations[j] + s[i,j])**alpha - (origins[i] + s[i,j])**alpha) * (origins[i]**alpha + 1)
                denominator = ((origins[i] + s[i,j])**alpha + 1) * ((origins[i] + destinations[j] + s[i,j])**alpha + 1)
                P[i,j] = numerator/denominator
    else:
        numerator = ((s + origins + destinations.T)**alpha - (s + origins)**alpha) * (origins**alpha + 1)
        denominator = ((s+origins)**alpha + 1) * ((s + origins  + destinations.T)**alpha + 1)
        P = np.divide(numerator,denominator)

    np.fill_diagonal(P, 0.0)

    # do row normalization, i.e. make each row sum to 1
    if normalize: 
        rowSums = np.sum(P,axis=1).reshape(-1,1)
        P = P/rowSums

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P


def radiationModel(origins, destinations, s, zeroDiagonal=False, normalize=True):

    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"

    n = origins.shape[0]
    m = destinations.shape[0]

    assert len(s.shape) == 2 and s.shape[0] == n and s.shape[1] == m

    origins = origins.astype(np.float32)

    numerator = np.dot(origins,destinations.T)

    denominator1 = s + origins
    denominator2 = s + origins + destinations.T

    denominator = denominator1 * denominator2

    P = np.divide(numerator,denominator)

    if zeroDiagonal:
        assert n==m, "Zeroing the diagonal only makes sense in a square matrix"
        np.fill_diagonal(P, 0.0)

    if normalize:
        rowSums = np.sum(P,axis=1).reshape(-1,1)
        P = P/rowSums

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P


def gravityModel(origins, destinations, d, alpha, decay="power", zeroDiagonal=False, normalize=True):
    
    assert len(origins.shape) == 2 and origins.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"
    assert len(destinations.shape) == 2 and destinations.shape[1] == 1, "`origins` and `destinations` must be 2D with a single column"

    n = origins.shape[0]
    m = destinations.shape[0]

    assert len(d.shape) == 2 and d.shape[0] == n and d.shape[1] == m

    origins = origins.astype(np.float32)
    d = d.astype(np.float32)

    numerator = np.dot(origins,destinations.T)
    
    denominator = None
    if decay=="power":
        denominator = d**(alpha)
    elif decay=="exponential":
        denominator = np.exp(d*alpha)
    else:
        raise ValueError("`decay` must be either 'power' or 'exponential'")

    P = np.divide(numerator,denominator)

    if zeroDiagonal:
        assert n==m, "Zeroing the diagonal only makes sense in a square matrix"
        np.fill_diagonal(P, 0.0)

    if normalize:
        rowSums = np.sum(P,axis=1).reshape(-1,1)
        P = P/rowSums

    P[np.isnan(P) | np.isinf(P)] = 0.0
    assert not np.any(np.isnan(P))
    assert not np.any(np.isinf(P))

    return P

def getInterveningOpportunities(features, distanceMatrix, slowMode=False):
    assert len(features.shape) == 2
    assert features.shape[1] == 1

    n = features.shape[0]

    assert len(distanceMatrix.shape)==2
    assert distanceMatrix.shape[0] == distanceMatrix.shape[1]
    assert distanceMatrix.shape[0] == n

    S = np.zeros((n, n), dtype=np.float32)
    
    if slowMode:
        # naively iterate over all locations, sort distances to others, assign intervening opportunities
        for i in range(n):
            otherPatches = []
            for j in range(n):
                otherPatches.append((distanceMatrix[i,j], j))
            otherPatches.sort(key=lambda x: x[0]) # this is a stable sort

            cumSum = 0.0
            for distance, j in otherPatches[1:]:
                S[i,j] = cumSum
                cumSum += features[j]
    else:
        # Very important that we use mergesort here as it is a stable sort
        d = np.argsort(distanceMatrix, kind="mergesort", axis=1)

        for i in range(n):
            tempFeatures = features[d[i]]
            newFeatures = [0,0] + list(np.cumsum(tempFeatures[1:-1]))
            S[i,d[i]] =  newFeatures

    return S


if __name__ == "__main__":
    import time

    n = 120
    m = 80

    o = np.random.randint(0,5,size=(n,1)).astype(float)
    d = np.random.randint(0,5,size=(m,1)).astype(float)
    s = np.random.randint(0,5,size=(n,m)).astype(float)

    np.set_printoptions(precision=2,suppress=True)

    startTime = float(time.time())
    P1 = extendedRadiationModel(o,d,s,1.2,longForm=False,normalize=True)
    #print P1
    print time.time() - startTime

    startTime = float(time.time())
    P2 = extendedRadiationModel(o,d,s,1.2,longForm=True,normalize=True)
    #print P2
    print time.time() - startTime

    assert np.all(np.abs(P1-P2) < 0.0001)

    
    '''
    a = np.random.randint(1,1000,size=(n,1))

    def hasUniqueRows(m):
        for i in range(m.shape[0]):
            if len(set(m[i,:])) != len(m[i,:]):
                return False
        return True
    
    d = np.random.randint(0,100000,size=(n,n))
    d += d.T
    np.fill_diagonal(d,0)  
    while not hasUniqueRows(d):
        print "Rechecking"
        d = np.random.randint(1,n**3,size=(n,n))
        d += d.T
        np.fill_diagonal(d,0)


    startTime = float(time.time())
    S = getInterveningOpportunities(a,d)
    print time.time() - startTime
    
    startTime = float(time.time())
    S2 = getInterveningOpportunitiesSlow(a,d)
    print time.time() - startTime

    assert np.all(np.abs(S-S2) == 0)
    '''

    pass