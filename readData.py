import streamlit as st
import geopandas as gpd
import os
import pyproj
import folium # map rendering library
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values
from streamlit_folium import folium_static
from shapely.geometry import Point

#-------------------------------------------------
def center(address):
    """
    address:= Enter Location name  
    """
    geolocator = Nominatim(user_agent="id_explorer")
    location = geolocator.geocode(address)
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude


def color_coder(flood_type):
    """
    Color coder for different flood types
    param: flood_type: str
    """
    if flood_type == 'Rivers and Sea':
        return 'blue'
    else:
        return 'orange'
#---------------------------------------------------
@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def read_historic_floods(path):
    print('Adding Historic floods')
    gdf = gpd.read_file(path)
    gdf_crs  = gdf.to_crs(epsg=4326)
    return gdf_crs


@st.cache(allow_output_mutation=True,suppress_st_warning=True)
def read_data(path):
    st.write('Reading Raw Data')
    gdf = gpd.read_file(path)
    gdf['centroids'] = gdf.centroid.to_crs(pyproj.CRS.from_epsg(4326))
    gdf.to_crs(pyproj.CRS.from_epsg(4326), inplace=True)
    #gdf['centroid_4326'] = gdf.centroid
    gdf['centroid_4328'] = gdf.to_crs(pyproj.CRS.from_epsg(4328)).centroid#.to_crs(pyproj.CRS.from_epsg(4326))
    gdf = gdf[1:]
    return gdf

def add_layer(
                    gdf,
                    map,
                    pop_name,
                    layer_name,
                    color,
                    centroids = False,show = False):
    
    fg=folium.FeatureGroup(name= layer_name, show=show)
    
    for _, r in gdf.iterrows():
        color_code = color_coder(r['flood_source'])
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                            style_function=lambda x: {'fillColor': 'grey','color': '#0b5394','dashArray': '5, 5'})
        folium.Popup(r[pop_name]).add_to(geo_j)
        geo_j.add_to(fg)
        if centroids:
            folium.Marker(location=[r['centroids'].y, r['centroids'].x],icon=folium.Icon(color=color_code),
                  popup='Name: {}'.format(r['fra_name'])).add_to(fg)
    map.add_child(fg)
    


def render_asset(input_address,map_sby,body):
    in_lat,in_log = center(input_address)
    folium.LayerControl().add_to(map_sby)
    folium.CircleMarker(location=[in_lat, in_log],radius=20, fill_color='yellow',color='red',
                  popup='Asset: {}'.format(input_address)).add_to(map_sby)
    with body:  
        folium_static(map_sby)

def calculate_risk(gdf,input_address):
    in_lat,in_log = center(input_address)
    geo_point = Point(in_log,in_lat)
    gdf['flag'] = gdf.contains(geo_point)
    gdf['Distance'] = gpd.GeoSeries(gdf.centroid_4328).distance(geo_point)

    dis_col = ['fra_name', 'frr_cycle', 'flood_source', 'Shape_Area','flag'] #'Distance',

    gdf_out = gdf[gdf.flag== True][dis_col]
    gdf_out.columns  = ['Name', 'Flood Risk Cycle', 'Source', 'Area','Is in risk']
     
    return gdf_out
    