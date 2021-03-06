#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Usage: python getGlobalMigrationStats.py

This script calculates year by year global statistics on the Global migration data, and graphs the total number of migrants over time.

It writes output/GLOBAL/migrationStats.csv and output/GLOBAL/numberOfMigrationsOverTime.png
'''

import time
import matplotlib.pyplot as plt
plt.style.use("seaborn-paper")

import numpy as np

from MigrationDataGlobal import getMigrationMatrix

def main():
    years = range(1960,2001,10)
    totalNumberOfMigrants = []

    f = open("output/GLOBAL/migrationStats.csv","w")
    f.write("Year,Number of countries without outgoing migrants,Number of countries without incoming migrants,Number of countries without incoming or outgoing,Total number of migrants\n")
    for year in years:
        print("Processing migration matrix for year %d" % (year))
        print("-" * 50)
        
        startTime = float(time.time())
        T = getMigrationMatrix(year,verbose=True)

        np.fill_diagonal(T,0) #we don't ever consider self migrations

        rowSums = T.sum(axis=1) 
        colSums = T.sum(axis=0)

        zeroOutgoing = rowSums==0
        zeroIncoming = colSums==0
        zeroBoth = zeroOutgoing & zeroIncoming # mask for when a country has 0 outgoing and 0 incoming migrants

        print("Number of countries with no outgoing migrants: \t%d" % zeroOutgoing.sum())
        print("Number of countries with no incoming migrants: \t%d" % zeroIncoming.sum())
        print("Number of countries without any migrations:    \t%d" % zeroBoth.sum())
        print("")
        print("Total number of migrants: %d" % (T.sum()))

        f.write("%d,%d,%d,%d,%d\n" % (year, zeroOutgoing.sum(), zeroIncoming.sum(), zeroBoth.sum(), T.sum()))

        totalNumberOfMigrants.append(T.sum())

        print("Finished loading and saving raw migration data for %d in %0.4f seconds" % (year, time.time()-startTime))
        print("\n\n")
    f.close()

    # Plot the total number of migration trips for each year
    plt.figure(figsize=(6,4))
    plt.plot(years,totalNumberOfMigrants)
    plt.title("Number of migrants over time", fontsize=14)
    plt.xlabel("Year")
    plt.ylabel("Number of migrants")
    plt.savefig(
        "output/GLOBAL/numberOfMigrationsOverTime.png",
        dpi=150,
        bbox_inches='tight',
        pad_inches=0
    )
    plt.close()

if __name__ == '__main__':
    print(__doc__)
    print("")
    main()