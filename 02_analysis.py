# Setup
import pandas as pd
import numpy as np
import requests
import geopandas as gpd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from sklearn.metrics import confusion_matrix, classification_report

# load randomly sampled points
rand_pts= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\random_points_manhattan_100000.geojson")

# load ecocomm
ecocomm= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\ecocomm_poly\ecocomm_poly_wet.geojson")\
            .set_crs("epsg:32618", allow_override = True).to_crs("epsg:4326")
ecocomm

df_1_ecocomm= gpd.sjoin(rand_pts, ecocomm, how="left", op="intersects")
assert df_1_ecocomm.shape[0] == 100000
assert len(df_1_ecocomm["DN"].unique()) > 1

# create indicators for 1609 wetland or water communities
df_1_ecocomm["DN"].unique()
df_1_ecocomm["WETLAND"]= (df_1_ecocomm["DN"] == 608).astype(int)
df_1_ecocomm["WATER"]= (df_1_ecocomm["DN"] == 600).astype(int)

df_1_ecocomm.drop(["index_right"], axis=1, inplace=True)
# load fema floodplains
floodplain100= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\floodplain_100_clipped_dissolved.geojson")
floodplain500= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\floodplain_500_clipped_dissolve.geojson")

df_1_fema100= gpd.sjoin(df_1_ecocomm, floodplain100, how="left", op="intersects")
df_1_fema100["FLOODPLAIN_100"]= (df_1_fema100["index_right"].notna()).astype(int)
df_1_fema100.columns

df_1_fema= gpd.sjoin(df_1_fema100.drop(["index_right"], axis=1), \
            floodplain500, how="left", op="intersects")
df_1_fema["FLOODPLAIN_500"]= (df_1_fema["index_right"].notna()).astype(int)

# Load data on deep and contiguous flooding
# fixed invalid geometries
# has a 15ft buffer, and polygons dissolved
flood_storm= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\moderate_flood_dissolve_test.geojson")\
    .set_crs("epsg:2263", allow_override = True).to_crs(4326)

 # checking that geometry dissolved correctly and is not null
fig, ax = plt.subplots(1, 1, figsize=(12, 12))
flood_storm["geometry"].plot(ax = ax)
plt.axis('off')

df_1_storm= gpd.sjoin(df_1_fema.drop("index_right", axis = 1), flood_storm, how="left", op="intersects")
df_1_storm["FLOOD_STORMWATER"]= (df_1_storm["index_right"].notna()).astype(int)

assert len(df_1_storm["FLOOD_STORMWATER"].unique()) > 1
df_1_storm["FLOOD_STORMWATER"].value_counts()
# select only relevant variables
df_selection= df_1_storm[["id_left", "WETLAND", "WATER", "FLOODPLAIN_100", "FLOODPLAIN_500",\
                            "FLOOD_STORMWATER","geometry"]]

# check selection shape
assert df_selection.shape[0] == 100000

# create training and test data
df_sel_1 = df_selection.head(70000)
df_sel_2 = df_selection.tail(30000)

# Load CDs, for merging and aggregating later
cds= gpd.read_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\Manhattan_CDs.geojson")

df_sel_2_cds= gpd.sjoin(df_sel_2, cds, how = "left", op = "intersects")
df_sel_2_cds= df_sel_2_cds[df_sel_2_cds["boro_cd"].notna()]

assert len(df_sel_1["WETLAND"].unique()) > 1
assert len(df_sel_1["WATER"].unique()) > 1
assert len(df_sel_1["FLOODPLAIN_100"].unique()) > 1

################################################################################
# OUTCOME: 100-YEAR FLOODPLAIN
################################################################################

# Fit logistic regression model
model = smf.glm(formula = "FLOODPLAIN_100 ~ WETLAND + WATER", \
        data=df_sel_1, family=sm.families.Binomial())
result = model.fit()
print(result.summary())

predictions = result.predict(df_sel_2_cds[["WETLAND", "WATER"]]).rename("PREDICTION")
predict_df_floodplain= df_sel_2_cds.merge(predictions, left_index = True, right_index = True)
predict_df_floodplain["PREDICT_SUCCESS"] = (predict_df_floodplain["PREDICTION"] > 0.5).astype(int)

# Classification report
print(classification_report(predict_df_floodplain["FLOODPLAIN_100"] ,
                            predict_df_floodplain["PREDICT_SUCCESS"],
                            digits = 3))

y= predict_df_floodplain.groupby(["boro_cd"])["PREDICT_SUCCESS"].mean()
x= df_sel_2_cds.groupby(["boro_cd"])["FLOODPLAIN_100"].mean()

# Plotting success
plt.xlabel('Actual Flooding Rate by Community District')
plt.ylabel('Predicted Flooding Rate by Community District')
plt.scatter(x, y, color = 'blue')
plt.savefig(r"C:\Users\Jennah\Desktop\QGIS\proj1\Map PDFs\fig1.pdf")

x.sort_values(ascending = False).head(5)

y.sort_values(ascending = False).head(5)

################################################################################
# OUTCOME: DEEP AND CONTIGUOUS STORMWATER FLOODING
################################################################################
# Fit logistic regression model
model = smf.glm(formula = "FLOOD_STORMWATER ~ WETLAND + WATER", \
        data=df_sel_1, family=sm.families.Binomial())
result = model.fit()
print(result.summary())

predictions = result.predict(df_sel_2_cds[["WETLAND", "WATER"]]).rename("PREDICTION")
predict_df_storm= df_sel_2_cds.merge(predictions, left_index = True, right_index = True)
predict_df_storm["PREDICT_SUCCESS"] = (predict_df_storm["PREDICTION"] > 0.4).astype(int)

# Classification report
print(classification_report(predict_df_storm["FLOOD_STORMWATER"],
                            predict_df_storm["PREDICT_SUCCESS"],
                            digits = 3))

predict_df_storm.columns
x= predict_df_storm.groupby(["boro_cd"])["PREDICT_SUCCESS"].mean()
y= df_sel_2_cds.groupby(["boro_cd"])["FLOOD_STORMWATER"].mean()

# Plotting success
plt.ylabel('Actual Flooding Rate by Community District')
plt.xlabel('Predicted Flooding Rate by Community District')
plt.scatter(x, y, color = 'blue')
plt.show()

x.sort_values(ascending = False).head(5)
y.sort_values(ascending = False).head(5)

stormwater_comp= (predict_df_storm.groupby(["boro_cd"])["PREDICT_SUCCESS"].mean().div(predict_df_storm.groupby(["boro_cd"])["FLOOD_STORMWATER"].mean()))
floodplain_comp= (predict_df_floodplain.groupby(["boro_cd"])["PREDICT_SUCCESS"].mean().div(predict_df_floodplain.groupby(["boro_cd"])["FLOODPLAIN_100"].mean()))
# Save geodataframe comparing success rates
# Scores of 1 mean that the rate is correctly predicted
# > 1 or < 1 indicates a mismatch in rates
cds_output= cds.merge(stormwater_comp.rename("SUCCES COMP STORMWATER"),\
            right_index = True, left_on = "boro_cd")\
            .merge(floodplain_comp.rename("SUCCESS COMP FLOODPLAIN"),\
                        right_index = True, left_on = "boro_cd")

cds_output
cds_output.to_file(r"C:\Users\Jennah\Desktop\QGIS\proj1\Data\reg_output_success.geojson", driver = "GeoJSON")
