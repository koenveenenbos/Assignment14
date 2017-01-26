# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 09:02:07 2017

@author: Tim Jak & Koen Veenenbos 
Team: JakVeenenbos
"""

from twython import Twython
import os, ogr, osr
import json
import folium
import subprocess

# Codes to access twitter API. 
APP_KEY = 'ECkIe7bXJACY12Auje2hV30ih'
APP_SECRET = 'uZHpd3FkfD7d2h1ozBpypsm9Nroq96yqmmFGFTOfUVkAgPYsn6'
OAUTH_TOKEN = '3077436986-XEP6brlHg0pqOKbvxw7BzAJR2nqutCmlYcHFQoM'
OAUTH_TOKEN_SECRET = 'CEhbkzfDywZZLUE5a5PlsoaImufT2UyAlkhjFHfD2Y11M'

# Initiating Twython object 
twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

# Define location and ratio
longtitude = 52.3702157
latitude = 4.8951679
ratio = 250
countnumber = 100

# Search for tweets
search_results = twitter.search(q='#schaatsen', geocode='%f,%f,%dkm' % (longtitude, latitude, ratio), count='%d' % (countnumber))

#Create an empty list
coords=[]

#Retrieve the coordinates and the username per tweet (if coordinates are available)
for tweet in search_results["statuses"]:
    username =  tweet['user']['screen_name']
    coordinates = tweet['coordinates']
    if coordinates != None:
        lat = tweet['coordinates']['coordinates'][0]
        lon = tweet['coordinates']['coordinates'][1]
        coords += [(float(lat), float(lon))]

#Set layer, driver and file name
layername = "schaatsplaats"
driverName = "ESRI Shapefile" 
drv = ogr.GetDriverByName(driverName)
filename = "schaatsplaats.shp"
datasource = drv.CreateDataSource(filename)

#Apply the right coordinate system to the points
spatialReference = osr.SpatialReference()
spatialReference.ImportFromEPSG(4326)
layer=datasource.CreateLayer(layername, spatialReference, ogr.wkbPoint)
layerDefinition = layer.GetLayerDefn()

#Create a point per set of coordinates
for coord in coords:
        schaats_point = ogr.Geometry(ogr.wkbPoint)
        schaats_point.SetPoint(0, coord[0], coord[1])
        schaats_feature = ogr.Feature(layerDefinition)
        schaats_feature.SetGeometry(schaats_point)
        layer.CreateFeature(schaats_feature)

#Destroy datasource to get the shapefile      
datasource.Destroy()

#Create a geoJSON file of the point shapefiles
bash = 'ogr2ogr -f GeoJSON -t_srs crs:84 schaatsplaats.geojson schaatsplaats.shp'
schaatsgeojson = subprocess.Popen(bash, shell=True)

#Plot the points in a nice map!
schaatsGeo=os.path.join("schaatsplaats.geojson")
map_points = folium.Map(location=[52,5.7],tiles='Mapbox Bright', zoom_start=6)
map_points.choropleth(geo_path=schaatsGeo)
map_points.save('schaats_points.html')