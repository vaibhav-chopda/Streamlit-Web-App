import pandas as pd # library for data analsysis
#import json # library to handle JSON files
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
#import requests # library to handle requests
import numpy as np
import folium # map rendering library
import streamlit as st
from streamlit_folium import folium_static
import os
import geopandas as gpd
from shapely.geometry import Point
import pyproj


st.set_page_config(layout="wide", page_icon=":location:", page_title="Flood Risk")

#------------------------------------------------
def set_proxy():
    #    user='user_example', passwd='pass_example', 
    #    address='address_example', port=int('port_example'))
    proxy_addr = 'X'

    os.environ['http_proxy'] = proxy_addr
    os.environ['https_proxy'] = proxy_addr

def unset_proxy():
    os.environ.pop('http_proxy')
    os.environ.pop('https_proxy')
#-------------------------------------------------

@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def read_data():
    st.write('Reading Raw Data')
    gdf = gpd.read_file(r'Flood_Risk_Areas.json')
    gdf['centroids'] = gdf.centroid.to_crs(pyproj.CRS.from_epsg(4326))
    gdf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    #gdf['centroid_4326'] = gdf.centroid
    gdf['centroid_4328'] = gdf.to_crs(pyproj.CRS.from_epsg(4328)).centroid#.to_crs(pyproj.CRS.from_epsg(4326))
    gdf = gdf[1:]
    return gdf

def color_coder(flood_type):
    if flood_type == 'Rivers and Sea':
        return 'blue'
    else:
        return 'orange'


def center(address):
    geolocator = Nominatim(user_agent="id_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude

def render_asset(input_address,map_sby,body):
    in_lat,in_log = center(input_address)
    folium.CircleMarker(location=[in_lat, in_log],radius=20, fill_color='yellow',color='red',
                  popup='Asset: {}'.format(input_address)).add_to(map_sby)
    #print('INFO: Added Asset {} to Map'.format(input_address))
    with body:
        folium_static(map_sby,width = 1100)

def add_polygon(gdf,map_sby):
    for _, r in gdf.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                            style_function=lambda x: {'fillColor': 'orange'})
        folium.Popup(r['fra_name']).add_to(geo_j)
        geo_j.add_to(map_sby)
        #Adding Centroid of Risk Area
        folium.Marker(location=[r['centroids'].y, r['centroids'].x],icon=folium.Icon(color=color_coder(r['flood_source'])),
                  popup='Name: {}'.format(r['fra_name'])).add_to(map_sby)
                  #length: {} <br> area: {} <br>r['Shape_Length'], r['Shape_Area']

def calculate_risk(gdf,input_address):
    in_lat,in_log = center(input_address)
    geo_point = Point(in_log,in_lat)
    gdf['flag'] = gdf.contains(geo_point)
    gdf['Distance'] = gpd.GeoSeries(gdf.centroid_4328).distance(geo_point)

    dis_col = ['fra_name', 'frr_cycle', 'flood_source', 'Shape_Area','flag'] #'Distance',

    gdf_out = gdf[gdf.flag== True][dis_col]
    gdf_out.columns  = ['Name', 'Flood Risk Cycle', 'Source', 'Area','Is in risk']
     
    return gdf_out

##Reading Data 
gdf_raw  = read_data()
gdf  = gdf_raw
#Get Proxy to get address
#set_proxy()


############################################################################  SIDEBAR  ############################################################################
st.sidebar.write("Use the widgets to alter the map:")

select_maps = st.sidebar.selectbox(
    "What data do you want to see?",
    ("OpenStreetMap", "Stamen Terrain","Stamen Toner")
)
input_address = st.sidebar.text_input("Enter Asset Location", key="Address",value='London, UK')
lat,long = center(input_address) #Got the lat & lon

############################################################################  INTIALIZE MAP  ############################################################################
map_sby = folium.Map(tiles=select_maps, location=[lat, long], zoom_start=8)

html_temp = """
	<h1 style ="color:black;text-align:center;"> Map Of {} </h1>

	""".format(input_address)
	
	# this line allows us to display the front end aspects we have
	# defined in the above code
st.markdown(html_temp, unsafe_allow_html = True)

make_map_responsive= """
 <style>
 [title~="st.iframe"] { width: 100%}
 </style>
"""
st.markdown(make_map_responsive, unsafe_allow_html=True)

############################################################################  ADDING POLYGON TO MAP  ############################################################################

add_polygon(gdf,map_sby)
sep, body, sep2 = st.columns((1,3,1))

render_asset(input_address,map_sby,body)


############################################################################  CALCULATE RISK FROM POLYGON  ############################################################################

gdf_out = calculate_risk(gdf,input_address)
#print(gdf_out.head(5))

st.table(gdf_out.head(5))

