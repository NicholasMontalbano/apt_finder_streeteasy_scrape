import pandas as pd
import geopandas as gpd
import re
from shapely import wkt

import faulthandler
faulthandler.enable()

# Read in the data -----------------------

### Park Equity GeoJSON
url = "https://raw.githubusercontent.com/NewYorkCityCouncil/park_equity_covid_2022/main/data/processed/ct_grouped.geojson"
parks = gpd.read_file(url)

### Park Equity GeoJSON
ct = parks[['GEO_ID', 'BoroName', 'geometry']]

### Open Data NYPD Arrests (YTD)
# https://data.cityofnewyork.us/Public-Safety/NYPD-Arrest-Data-Year-to-Date-/uip8-fykc
url = 'https://data.cityofnewyork.us/api/geospatial/uip8-fykc?method=export&format=GeoJSON'
safety = gpd.read_file(url)

### apt_csv data
apt_csv = pd.read_csv('data/apt_csv.csv')
apt_csv['lat'] =  [re.sub(',-[0-9.]+', '', str(x)) for x in apt_csv['geo']]
apt_csv['lon'] =  [re.sub('[0-9.]+,', '', str(x)) for x in apt_csv['geo']]
apt_geo = gpd.GeoDataFrame(
    apt_csv, geometry=gpd.points_from_xy(apt_csv['lon'], apt_csv['lat']))

### Make sure crs match
apt_geo.crs = parks.crs
safety.crs = parks.crs

# Spatial join data -----------------------

### Parks and safety
ct_safety = ct.sjoin(safety, how="left").groupby('GEO_ID').size().to_frame('arrests').reset_index()
ct_safety['GEO_ID'] = ct_safety['GEO_ID'].apply(str)
parks_safety = parks.merge(ct_safety, on = "GEO_ID", how="left")

### Apartments and parks
apt_metrics = apt_geo.sjoin(parks_safety, how="left")
apt_metrics = apt_metrics.drop(['index_right'], axis = 1)
apt_metrics['arrests_pc'] = apt_metrics['arrests'] / apt_metrics['population']
apt_metrics.drop(['lat', 'lon', 'avg_hrs_sum', 'hrs_per_facre', 'hrs_per_tacre', 'hrs_per_pc', 'perc_foreign', 'perc_nhwhite', 't_acre_sum', 't_acre_sum_uncap', 't_acre_pc'], axis=1, inplace=True)

# Write as GeoJSON -----------------------
apt_metrics.to_file('data/apt_metrics.geojson', driver='GeoJSON')

# Write as csv -----------------------
apt_metrics.drop(['geometry'],axis=1).to_csv('data/apt_metrics.csv', index=False) 