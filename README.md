# migration-lib
Python library for interfacing with the USA IRS Tax Stats migration data.

See [https://www.irs.gov/uac/soi-tax-stats-migration-data](https://www.irs.gov/uac/soi-tax-stats-migration-data) for more information about the data.

# Getting the data

This library is for interacting with the county-to-county IRS Tax-Stats migration data. In order to use it you will need to download the data, format it, and place it in the `data/USA/` directory.

We provide two ways to do this.
1. You can download [our copy of the pre-packaged data](https://dl.dropboxusercontent.com/u/45223629/USA.zip), and unzip it to `data/USA/`.

2. You can download the individual county-to-county zip files provided on the [Tax Stats webpage](https://www.irs.gov/uac/soi-tax-stats-migration-data). `MigrationData.py` expects to find the data such as `data/USA/<year>/<countyInFlows>` and `data/USA/<year>/<countyOutFlows>`. See `YEAR_FN_MAP` in `MigrationData.py` for how to name all the files (or as the place to edit to suit your needs). The 2005-2006 data is a special case with more details below.

## USA 2005-2006 Migration Flows

The 2005-2006 County-to-County migration flows from the IRS website are incomplete, the zip file can be downloaded, however the data is missing. We contacted the Tax Stats group to get the correct data. This data can be found in [data/countymigration0506.zip](data/countymigration0506.zip).

