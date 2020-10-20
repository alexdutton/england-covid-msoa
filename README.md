# MSOA-level COVID-19 case count time series data

These data are weekly totals for new COVID-19 cases published daily for England by MSOA ([Middle Level Super Output
Area](https://en.wikipedia.org/wiki/ONS_coding_system#Neighbourhood_Statistics_Geography)).

Data in this repository start from the 2–8 October period.

These data were originally pulled from the ArcGIS API, but from the 16th October are now pulled from
the endpoint used by the [new interactive
map](https://coronavirus-staging.data.gov.uk/details/interactive-map).

## Why?

I originally couldn't find historical granular data anywhere, and wanted to be able to track numbers in my local area.

I've now found that PHE/NHSX [publish historical weekly data](https://coronavirus-staging.data.gov.uk/details/about-data#downloads)
but this is still not the entire dataset. That data has one value per week, whereas this is collecting daily rolling
sums for week-long periods. This data will also track revisions to previously-released data.


## Data files

The `data/` directory contains:

### data/observations.csv

A CSV file of all MSOA-level data points with the following columns:

* `msoa` — The MSOA code
* `source` — Either `arcgis` or `api`, corresponding to which API the data was pulled from. `arcgis` is from when the
  data were published in an ArcGIS dashboard, and `api` from when the cases map was moved to
  [coronavirus.data.gov.uk](https://coronavirus-staging.data.gov.uk/details/interactive-map).
* `specimenDate` — The end date of the period for which tests are counted in this observation.
* `observationDate` — The date reported by the API for when the tests were counted. It's possible to have multiple rows
  for a given specimen date and different observation dates if test results for the same day are reported at different
  times.
* `fetchDate` — When the data were fetched from the API
* `rollingSum` — The number of positive tests for this MSOA in the 7 day period up to and including the `specimenDate`.
  i.e. if `specimenDate` is `2020-10-20`, then the rolling sum covers the period from the 14th to the 20th of October.
 


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

### data/geometries.json

The geometry data pulled from the ArcGIS API. These are all rough polygons, and probably not in a standard format.
It would be trivial to convert them to GeoJSON though, or for users of this data to match up the MSOA codes to
geometries from elsewhere (e.g. from [MapIt](https://mapit.mysociety.org/areas/OMF.html)).


## Updating

These data are currently fetched, committed and pushed manually, The module for fetching new data is
`england_covid_msoa.update_observations_from_api`.  Data updates generally happen late afternoon.

I'm doing it manually so I can check that things are working properly each
time, as I fully expect to have not anticipated some aspect of the data or API,
or for the API to change from under me at some point.


## If you run this API

I couldn't see how to get batch data out of any API or download on
api.coronavirus.data.gov.uk at the MSOA level for individual days, so I've resorted to making a
request for every single MSOA, with a 0.2s hard-coded interval between
requests. If my script is causing you trouble, please get in touch and let me
know how I can do things better for you.
