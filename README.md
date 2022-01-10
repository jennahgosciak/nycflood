# Analysis of flooding in Manhattan compared to the island's ecology in 1609

* See [Medium](https://jennahgosciak.medium.com/what-makes-a-floodplain-1e9e28cc8d6f) for the article based on this analysis.
* Most of the analysis was done in QGIS and is not reproducible. Data prep and logistic regressions were done in Python.
* For more information, see the [technical methodology](https://github.com/jennahgosciak/nycflood/blob/main/methodology.md).


1. [00_convert_esri_grid.py](https://github.com/jennahgosciak/nycflood/blob/main/00_convert_esri_grid.py)
  * Converts an ESRI grid file into a raster (tif) file with recoded and coarsened values.
2. [01_load_data.py](https://github.com/jennahgosciak/nycflood/blob/main/01_load_data.py)
  * Load data for 311 reports of flooding.
  * Filter to 311 reports that occurred the same day or the day after heavy rainfall.
3. [02_analysis.py](https://github.com/jennahgosciak/nycflood/blob/main/02_analysis.py)
  * Runs two logistic regressions. The goal is to evaluate the identify how well wetlands in 1609 predict present-day flooding.
