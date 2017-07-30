''' From https://www2.census.gov/geo/docs/maps-data/maps/reg_div.txt
'''

REGIONS = {
    "Northeast":{
        "New England": ["09", "23", "25", "33", "44", "50"],
        "Middle Atlantic": ["34", "36", "42"]
    },
    "Midwest":{
        "East North Central": ["17", "18", "26", "39", "55"],
        "West North Central": ["19", "20", "27", "29", "31", "38", "46"]
    },
    "South":{
        "South Atlantic": ["10", "11", "12", "13", "24", "37", "45", "51", "54"],
        "East South Central": ["01", "21", "28", "47"],
        "West South Central": ["05", "22", "40", "48"],
    },
    "West":{
        "Mountain": ["04", "08", "16", "30", "32", "35", "49", "56"],
        "Pacific": ["02", "06", "15", "41", "53"]
    }
}

REGION_NAMES = {
    "Northeast": 0,
    "Midwest": 1,
    "South": 2,
    "West": 3
}

REGION_NAMES_LIST = [
    "Northeast",
    "Midwest",
    "South",
    "West"
]

DIVISION_NAMES = {
    "New England": 0,
    "Middle Atlantic": 1,
    "East North Central": 2,
    "West North Central": 3,
    "South Atlantic": 4,
    "East South Central": 5,
    "West South Central": 6,
    "Mountain": 7,
    "Pacific": 8
} 

DIVISION_NAMES_LIST = [
    "New England",
    "Middle Atlantic",
    "East North Central",
    "West North Central",
    "South Atlantic",
    "East South Central",
    "West South Central",
    "Mountain",
    "Pacific"
]

def getRegion(fips):
    '''Returns the region that a particular county fips is from.'''
    for region, divisions in REGIONS.items():
        for division, keys in divisions.items():
            for key in keys:
                if fips.startswith(key):
                    return region
    
    raise ValueError("FIPS not found")

def getDivision(fips):
    '''Returns the census division that a particular county fips is from.'''
    for region, divisions in REGIONS.items():
        for division, keys in divisions.items():
            for key in keys:
                if fips.startswith(key):
                    return division
    
    raise ValueError("FIPS not found")


if __name__ == "__main__":

    from collections import Counter

    f = open("data/countyIntersection.txt","r")
    fipsCodes = f.read().strip().split("\n")
    f.close()

    regionCounts = []
    divisionCounts = []
    for fips in fipsCodes:
        region = getRegion(fips)
        division = getDivision(fips)

        regionCounts.append(region)
        divisionCounts.append(division)

    regionCounts = Counter(regionCounts)
    divisionCounts = Counter(divisionCounts)

    import numpy as np
    import matplotlib
    import matplotlib.pyplot as plt
    plt.style.use('ggplot')

    #----------------------------------------------------------------------------------
    # Graph the number of counties per region
    #----------------------------------------------------------------------------------
    plt.figure()

    xLabels = []
    yValues = []
    for label, value in regionCounts.items():
        xLabels.append(label)
        yValues.append(value)

    xTickLocations = np.array(range(len(xLabels)))

    plt.bar(xTickLocations, yValues, width=0.8)
    plt.xticks(xTickLocations+0.4, xLabels, rotation=25)

    plt.title("Number of Counties per Region", fontsize=18)
    plt.ylabel("Number of Counties", fontsize=16)

    plt.savefig("results/regionCounts.png", bbox_inches='tight')
    plt.close()


    #----------------------------------------------------------------------------------
    # Graph the number of counties per division
    #----------------------------------------------------------------------------------
    plt.figure()

    xLabels = []
    yValues = []
    for label, value in divisionCounts.items():
        xLabels.append(label)
        yValues.append(value)

    xTickLocations = np.array(range(len(xLabels)))

    plt.bar(xTickLocations, yValues, width=0.8)
    plt.xticks(xTickLocations+0.4, xLabels, rotation=25)

    plt.title("Number of Counties per Division", fontsize=18)
    plt.ylabel("Number of Counties", fontsize=16)

    plt.savefig("results/divisionCounts.png", bbox_inches='tight')
    plt.close()
