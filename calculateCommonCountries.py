#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Caleb Robinson <calebrob6@gmail.com>
#
# Distributed under terms of the MIT license.
'''
Usage: python calculateCommonCountries.py

This script calculates which country codes are shared between all of the years of migration data.

Creates output/global_country_list.txt which is an alphabetically sorted list of country codes in the World Bank Bilateral Migration Data that are common across all years of data.
'''
from MigrationDataGlobal import loadFile

def main():
    step = 10
    years = range(1960, 2000+step, step) # years for which we have data

    countryCodeSets = [] # a set for each year of data containing *all* the country codes from that year
    for i,year in enumerate(years):
        records = loadFile(year)

        countryCodeSet = set()
        for origin,destination,val in records:
            #origin = origin[-4:-1]
            #destination = destination[-4:-1]            

            countryCodeSet.add(origin)
            countryCodeSet.add(destination)
        countryCodeSets.append(countryCodeSet)

    # a set for each year of data containing the country codes filtered according to TODO
    newCountryCodeSets = []
    for i,year in enumerate(years):
        countryCodeSet = countryCodeSets[i]
        newCountryCodeSet = set()
        for countryCode in countryCodeSet:
            #perform filtering here
            newCountryCodeSet.add(countryCode)

        print("%d -- %d countries" % (year, len(newCountryCodeSet)))
        newCountryCodeSets.append(newCountryCodeSet)

    print("")

    # calculate the intersection of all sets
    joinedSet = set(newCountryCodeSets[0])
    for s in newCountryCodeSets[1:]:
        joinedSet.intersection_update(s)
    print("Total of %d countries that are common to all years of data." % (len(joinedSet)))

    print("")

    # sort FIPS code in numerical order
    joinedList = list(joinedSet)
    sortedJoinedList = sorted(joinedList)

    # write output
    outputFn = "output/global_country_list.txt"
    print("Saving list of country codes common to all years of data to %s" % (outputFn))
    f = open(outputFn, "w")
    for countryCode in sortedJoinedList:
        f.write("%s\n" % (countryCode))
    f.close()
    
    print("Finished")

if __name__ == '__main__':
    print(__doc__)
    print("")
    main()