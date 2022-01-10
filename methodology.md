# Technical methodology for Assignment 3:

1. Downloaded data sources:
  	1. [311 reports of heavy flooding](https://data.cityofnewyork.us/Social-Services/Street-flooding-map/euy6-dafe), downloaded from New York City Open Data.
  		  1. Data are only 2010-present.
  		  2. I excluded 311 calls with a year of 2021 for completeness.
  		  3. In the first map, I represented the data with the "heat map" symbology.

  	2. [NOAA data on precipitation](https://www.ncei.noaa.gov/access/services/data)
  	    1. Downloaded precipitation summary data for the Central Park weather station (USW00094728) for all days between 01/01/2010 to 12/31/2020
  	3. [FEMA Floodplain maps](https://data.cityofnewyork.us/Environment/Sea-Level-Rise-Maps-2020s-100-year-Floodplain-/ezfn-5dsb), downloaded from New York City Open Data
        1. These are estimates for the 2020s, provided by the Mayor's Office of Climate and Sustainability.
        2. I clipped these polygons to the 5 boroughs (they appeared to extend into the river).
        3. I noticed that these polygons overlap. For any area-based calculations I used versions with dissolved polygons.
        4. I changed the colors. The 500-year floodplain is a deeper blue; the 100-year floodplain is a lighter blue. I experimented with transparency, but instead I decided to later the 100-year floodplain on first and then the 500-year floodplain given that the 100-year floodplain is a more immediate risk.
  	4. [Moderate flooding associated with rainfall](https://data.cityofnewyork.us/City-Government/NYC-Stormwater-Flood-Map-Moderate-Flood/5rzh-cyqd).
        1. No transformations needed. I changed the symbology and added descriptive category names.
        2. I created a version of the data that excluded the high tides in 2050. I also exported the file as a geojson file since it original was in a geodatabase.
        3. I fixed geometries using the "Fix geometries" tool in QGIS.
        4. I created a version of the data that excluded the high tides in 2050 and had a 15 foot buffer.
        5. I used the dissolve tool in QGIS so that there were no overlapping polygons.

  	5. [Extreme flooding associated with rainfall](https://data.cityofnewyork.us/City-Government/NYC-Stormwater-Flood-Map-Extreme-Flood/w8eg-8ha6)
        1. No transformations needed. I changed the symbology and added descriptive category names.
        2. I created a version of the data that excluded the high tides in 2080.
  	6. Ecology of Manhattan in 1609
  	    1. Downloaded from the [Welikia project](https://welikia.org/download/scientific-data/)
  	    2. The primary datafile of interest was the ecocomm raster file. This was saved in the format of an ESRI grid file. I opened it in ArcMap in order to download the attribute table.
  	    3. I created coarsened categories of each of the ecological communities (there are 55 in total, I only saw 40 in the data). The categories I created were meant to describe the level of water in the original community. For example, was it marshland or a swamp (e.g. a wetland) or was it underwater?
  	    4. With these coarsened categories, I created a new raster file and mapped the old codes to the new codes. See this [google sheet](https://docs.google.com/spreadsheets/d/17u_WjWDV2KCcGdX5MQt_RIMrHQfEeQ00MhGHXAw6WHk/edit#gid=0) and 00_convert_esri_grid.py.
  	    5. I changed the symbology of these codes using a color scheme that seemed contextual (blue to represented water and orange to represent dry land) and I added descriptive categories.
  	    6. With these coarsened categories, I converted the raster file to a polygon.
  	    7. I produced an extract of the polygon file that is only wetland or water (numeric codes 600 and 608).
  	    8. I produced a version of the data clipped to polygon data for the 5 boroughs.
  	7. [5 boroughs polygon data](https://data.cityofnewyork.us/City-Government/Borough-Boundaries/tqmj-j8zm)
  		  1. No transformations needed.
  	8. [Community districts polygon data](https://data.cityofnewyork.us/City-Government/Community-Districts/yfnk-k7r4)
        1. Produced an extract of the data that only included community districts 3 and 11.
        2. Produced an extract of the data that was only for Manhattan (all community districts starting with 1).

  2.   Community-level analysis
  		 1. For the community-level analysis, I chose two community districts (community districts 3 and 11) that  appeared to have a high level of coverage by wetlands or   bodies of water. I also chose community district 3 given that it's where my family lives and I'm interested in the relationship between the history of the neighborhood as marshland and the current risk of flooding.
  		 2. Using the extract for community districts 3 and 11, I zoomed into each neighborhood and produced maps of the 4 different flooding measurements using the layouts manager in QGIS.
  		 3. I used the QGIS "Overlap analysis" tool to calculate the percentage of area covered by other layers. I did this in calculations of the percent of the community district's area covered by wetland or water in 1609 and in calculations of the percent of the community district's area covered by the 100- or the 500-year floodplain. For the second calculation, I used the version of the data that did not have overlaps (i.e. boundaries had been dissolved).
  		 4. I added a transparent layer, callouts, and rectangular frames in postprocessing.

3.   Statistical analysis
    1. I used a logistic regression (see 02_analysis.py) to estimate how well the 1609 ecology predicates flooding risk. I did this for both the FEMA 100-year floodplain and for the moderate risk of flooding due to rainfall.
    2. I first generated a random sample of 100,000 points that are in Manhattan (using Manhattan's modern-day boundaries) in QGIS.
    3. I then merged performed several spatial joins to existing polygon data (for ease of processing, I did this in Python).
        1. I merged to the FEMA 100-year floodplain using a spatial join with "intersects."
        2. I merged to the moderate risk of flooding polygon file (with a 15 ft buffer) using a spatial join with "intersects."
        3. I merged to the ecological communities file that had been filtered to wetlands and bodies of water using a spatial join With "intersects."
    4. With this merged file, I then split the data into two dataframes: one with 70,000 observations and the other with 30,000.
    5. I performed a logistic regression on the data with 70,000 observations and then using this model I estimated the predicted values with the data that had only 30,000. I compared the accuracy of these predicted values using a 50% threshold (i.e. if the predicted probability was > 50%, I coded that as a prediction of flooding).
    6. I compared the prediction of flooding to actual flooding at the community district level to observe variation and to see if these findings corroborated the community-level analysis.
