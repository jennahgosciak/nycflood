# load_dat.py
# Purpose: Loads data that requires some pre-processing steps

# Setup
import pandas as pd
import numpy as np
import requests
import geopandas as gpd
import matplotlib.pyplot as plt

# Load Open Data file of 311 street flooding reports
url = 'https://data.cityofnewyork.us/resource/wymi-u6i8.csv?$limit=200000'
flood311 = pd.read_csv(url)
assert flood311.shape[0] < 200000

# Convert to geodataframe
flood311_gdf = gpd.GeoDataFrame(flood311, geometry = gpd.points_from_xy(flood311.Longitude, flood311.Latitude))
flood311_gdf.head()

# Convert date to datetime
flood311_gdf["Created Date orig"] = flood311_gdf["Created Date"]
flood311_gdf["Created Date"] = pd.to_datetime(flood311_gdf["Created Date"])
# Check range
flood311_gdf["Created Date"].describe()

# filter out 2021
flood311_gdf= flood311_gdf[flood311_gdf["Created Date"].dt.year < 2021]

# Check only street flooding
assert flood311_gdf["Descriptor"].unique().tolist() == ["Street Flooding (SJ)"]
# Check no introduction of missing values
assert (flood311_gdf["Created Date"].isna() == flood311_gdf["Created Date orig"].isna()).all()

# Convert to date object (previously had time)
# For merging to rainfall data later
flood311_gdf["DATE"] = flood311_gdf["Created Date"].dt.date

# Plot of 311 reports by date
f = plt.figure()
f.set_figwidth(9)
f.set_figheight(6)

plt.plot(flood311_gdf["Created Date"].dt.date.value_counts().sort_index(),\
alpha = 0.8, color = "coral")
# naming the x and y axis
plt.xlabel('Date')
plt.ylabel('Number of 311 reports')

# load precipitation data from NCEI/NOAA
url = "https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&stations=USW00094728&startDate=2010-01-01&endDate=2020-12-31"
rainfall = pd.read_csv(url)
rainfall["DATE"] = pd.to_datetime(rainfall["DATE"])
assert (rainfall["DATE"].dt.year < 2021).all()
rainfall["DATE"]= rainfall["DATE"].dt.date
# check uniqueness
assert rainfall["DATE"].is_unique

# Plot 2
# Rainfall and flooding (in the same plot)
fig, ax1 = plt.subplots(figsize=(6,6))
plt.plot(rainfall["DATE"], rainfall["PRCP"], alpha = 0.8)
ax1.tick_params(axis='y')
ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

plt.plot(flood311_gdf["Created Date"].dt.date.value_counts().sort_index(),\
alpha = 0.8, color = "coral")
ax2.tick_params(axis='y')

# naming the x and y axis
plt.xlabel('Date')
ax1.set_ylabel('Precipitation in 1/10 mm')
ax2.set_ylabel('Number of 311 complaints')

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()

# filter flooding by date to see 311 reports associated with high levels of rain
rainfall_lgd= rainfall.copy()
rainfall_lgd["DATE"]= rainfall_lgd["DATE"] + pd.Timedelta(1, unit='D')
rainfall_lgd= rainfall_lgd[["DATE", "PRCP"]].rename(columns={"PRCP" : "PRCP_LGD"})
rainfall_merge= rainfall.merge(rainfall_lgd, how = "left", on = "DATE")

# 75th percentile threshold
rainfall_p75= rainfall["PRCP"].quantile(0.75)
rainfall_p75

flood311_rain= flood311_gdf.merge(rainfall_merge, how = "left", on = "DATE")
flood311_rain= flood311_rain.loc[(flood311_rain["PRCP"] >= rainfall_p75)\
                                    | (flood311_rain["PRCP_LGD"] >= rainfall_p75)]
flood311_rain

# Convert dates to string
flood311_gdf["DATE"]= flood311_gdf["DATE"].apply(lambda x: x.strftime('%Y-%m-%d'))
flood311_gdf["Created Date"]= flood311_gdf["Created Date"].apply(lambda x: x.strftime('%Y-%m-%d'))
flood311_rain["DATE"]= flood311_rain["DATE"].apply(lambda x: x.strftime('%Y-%m-%d'))
flood311_rain["Created Date"]= flood311_rain["Created Date"].apply(lambda x: x.strftime('%Y-%m-%d'))

# check data types, no weird dates
flood311_gdf.dtypes
flood311_rain.dtypes
flood311_rain.shape

# export as shapefile
flood311_gdf.to_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\Python Output\311 Flooding\flooding_311.shp")
flood311_rain.to_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\Python Output\311 Flooding\flooding_filt_rain.shp")
