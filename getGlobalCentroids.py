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

import fiona

#---------------------------------------------------------------------------------------------------
def main():
    progName = 'Get country centroids'
    print 'Starting %s' % (progName)
    startTime = float(time.time())


    f = open("output/global_country_list.txt")
    migrationCodes = []
    for line in f:
        line = line.strip()
        parts = line.split("|")
        code = parts[-1]
        migrationCodes.append(code)
    f.close()

    f = fiona.open("data/shapefiles/GLOBAL/TM_WORLD_BORDERS-0.3.shp")
    locations = {}
    for row in f:
        iso3 =  row["properties"]["ISO3"]
        lat,lon = float(row["properties"]["LAT"]),float(row["properties"]["LON"])
        locations[iso3] = (lat,lon)
    f.close()

    f = open("output/global_country_centroids.csv","w")
    f.write("ISO3CODE,lon,lat\n")
    for migrationCode in migrationCodes:
        lat,lon = locations[migrationCode]
        f.write("%s,%f,%f\n" % (migrationCode,lon,lat))
    f.close()

    print 'Finished in %0.4f seconds' % (time.time() - startTime)

if __name__ == '__main__':
    main()