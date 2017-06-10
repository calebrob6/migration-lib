# migration-lib
Python library for interfacing with the USA IRS Tax Stats migration data, and the World Bank Global Bilateral Migration database.

See [https://www.irs.gov/uac/soi-tax-stats-migration-data](https://www.irs.gov/uac/soi-tax-stats-migration-data) for more information about the IRS Tax Stats data.

See [http://data.worldbank.org/data-catalog/global-bilateral-migration-database](http://data.worldbank.org/data-catalog/global-bilateral-migration-database) for more information about the World Bank Global Bilateral Migration data.

# Datasets

We do not directly include the datasets that go with this library in this repository, but instead provide Dropbox downloads of relevant data. See the following sections for how to download and 

## Getting the IRS Tax Stats Migration data

In order to use `MigrationDataUSA.py` you will need to download the appropriate data, format it, and put it in the `data/MIGRATION/USA/` directory.

There are two good ways to do this.
1. You can download [our copy of the pre-packaged data](https://dl.dropboxusercontent.com/u/45223629/USA.zip), and unzip it to `data/MIGRATION/USA/`.

2. You can download the individual county-to-county zip files provided on the [Tax Stats webpage](https://www.irs.gov/uac/soi-tax-stats-migration-data). `MigrationDataUSA.py` expects to find the data such as `data/MIGRATION/USA/<year>/<countyInFlows>` and `data/MIGRATION/USA/<year>/<countyOutFlows>`. See `YEAR_FN_MAP` in `MigrationDataUSA.py` for how to name all the files (or as the place to edit to suit your needs). The 2005-2006 data is a special case with more details below.

### USA 2005-2006 Migration Flows Caveat

The 2005-2006 County-to-County migration flows from the IRS website are incomplete, the zip file can be downloaded, however the data is missing. We contacted the Tax Stats group to get the correct data. This data can be found in [data/countymigration0506.zip](data/countymigration0506.zip).

## Getting the World Bank Global Bilateral Migration data

In order to use `MigrationDataGlobal.py` you will need to download the appropriate data, format it, and put it in the `data/MIGRATION/GLOBAL/` directory.

There are two good ways to do this.
1. You can download [our copy of the pre-packaged data](https://dl.dropboxusercontent.com/u/45223629/GLOBAL.zip), and unzip it to `data/MIGRATION/GLOBAL/`.
2. You can download the raw data from [http://databank.worldbank.org/data/reports.aspx?source=global-bilateral-migration](http://databank.worldbank.org/data/reports.aspx?source=global-bilateral-migration).
    - Select all countries in the "Country Origin" option panel
    - Select all countries in the "Country Dest" option panel
    - Select "Total" in the "Migration By Gender"
    - Select all years in the "Year" option panel
    - Select "row", "column", "row", "page" as the options for the "Year", "Country Dest", "Country Origin", and "Migration by Gender" dropdowns respectively (in the "Layout" tab)
    - Download as an Excel file
    - Remove the two bottom most rows with the metadata content: "Data from database: Global Bilateral Migration", "Last Updated: ..."
    - Save as a CSV file, `data/MIGRATION/GLOBAL/migrationData.csv` with pipe delimiters (use the '|' character as a delimiter... or change the `MigrationDataGlobal.py` code)



# Shapefile Data

https://www.arcgis.com/home/item.html?id=3864c63872d84aec91933618e3815dd2