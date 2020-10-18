# MSOA-level COVID-19 case count time series data

These data are weekly totals for new COVID-19 cases published daily for England by MSOA ([Middle Level Super Output
Area](https://en.wikipedia.org/wiki/ONS_coding_system#Neighbourhood_Statistics_Geography)).

Data in this repository start from the 2–8 October period.

These data were originally pulled from the ArcGIS API, but from the 16th October are now pulled from
the endpoint used by the [new interactive
map](https://coronavirus-staging.data.gov.uk/details/interactive-map).

## Why?

I couldn't find historical granular data anywhere, and wanted to be able to track numbers in my local area.


## Data files

The `data/` directory contains:

### data/{date}.json

These are pretty much verbatim files from the ArcGIS API published on the date in the file name, with
geometries removed. There is a `wk{week}_{day}` field analogous to the [ISO week
date](https://en.wikipedia.org/wiki/ISO_week_date) format which contains the data for the 7 days up to and
including the day in the field name. i.e. `wk41_3` covers the period from 1 October to 7 October.

Note that the publication date is currently about four days behind the data. Use the field date, not the file date.

These files are kept in order to reconstruct other data files if later required. They are no longer created as the
data is no longer maintained in the ArcGIS API.

### data/{date}.csv

The same data as above as a CSV table.

### data/combined.csv

This file mirrors the form of the individual-date files, with a new column added for each new day's data.

### data/geometries.json

The geometry data pulled from the ArcGIS API. These are all rough polygons, and probably not in a standard format.
It would be trivial to convert them to GeoJSON though, or for users of this data to match up the MSOA codes to
geometries from elsewhere (e.g. from [MapIt](https://mapit.mysociety.org/areas/OMF.html)).


## Updating

These data are currently fetched, committed and pushed manually, The script for
fetching new data is `main.py`.  Data updates generally happen late afternoon.

I'm doing it manually so I can check that things are working properly each
time, as I fully expect to have not anticipated some aspect of the data or API,
or for the API to change from under me at some point.
