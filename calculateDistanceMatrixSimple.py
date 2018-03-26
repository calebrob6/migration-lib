#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Script for calculating a pairwise distance matrix from a csv file.

This script takes as input: a csv file where the first column is the primary key, the second column is the longitude, and the third column is the latitude.

It outputs a pairwise distance matrix between each of the rows in the input file.
This distance matrix will be in the same order as the list of GEOIDs to be included, and the distances will be in kilometers.
'''
import sys
import time

import numpy as np
import haversine
import scipy.spatial
import fiona
import shapely.geometry 

def main():

    if len(sys.argv) != 3:
        print("Usage: python calculateDistanceMatrix.py path/to/input.csv output/distanceMatrix.npy")
        return 
    
    print("Starting")
    startTime = float(time.time())

    inputFn = sys.argv[1]
    outputFn = sys.argv[2]

    f = open(inputFn,"r")
    headerline = f.readline().strip().split(",")
    print("Input file header: %s" % (headerline))
    data = []
    for line in f:
        line = line.strip()
        if line!="":
            parts=line.split(",")
            data.append((parts[0], float(parts[1]), float(parts[2])))
    f.close()

    coords = [(coord[2], coord[1]) for coord in data]

    distanceMatrix = scipy.spatial.distance.cdist(coords,coords,haversine.haversine)

    np.save(outputFn,distanceMatrix)
    
    print("Finished in %0.4f seconds" % (time.time()-startTime))

if __name__ == "__main__":
    main()