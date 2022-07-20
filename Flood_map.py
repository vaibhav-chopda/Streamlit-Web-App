import folium
import streamlit as st
from streamlit_folium import folium_static
from readData import *


st.set_page_config(layout="wide", page_icon="🗺️", page_title="Flood Risk Area") 
#flood_hist_path = r'Data\EA_HistoricFloodMap_SHP_Full.zip!data'

flood_data_path = r'Flood_Risk_Areas.json'

def _max_width_():
    max_width_str = f"max-width: 1400px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


#_max_width_()
html_temp = """
        <h1 style ="color:#012169;text-align:center;"> Map of {} </h1>

        """.format('England')
	
# this line allows us to display the front end aspects we have
# defined in the above code
#st.markdown(html_temp, unsafe_allow_html = True)

c30, c31, c32 = st.columns([2.5, 1, 3])

with c30:
    #st.image("logo.png", width=400)
    st.title("🗺️ Flood Risk Area UK")
    st.header("")

with st.expander("ℹ️ - About this app", expanded=True):

    st.write(
        """     
-   The *Flood Risk Map (UK)* app is an easy-to-use interface built in Streamlit!
-   Data is obtained from data.gov.uk. It assesses flooding scenarios as a result of rainfall with a 3.3 %, 1% and 0.1% chance of occurring each year. [Link](https://environment.data.gov.uk/DefraDataDownload/?mapService=EA/FloodRiskAreas&Mode=spatial)
	    """
    )

    st.markdown("")

st.markdown("")

    
##Reading Data 
gdf_raw  = read_data(flood_data_path)
gdf  = gdf_raw.copy()
#Get Proxy to get address
#set_proxy()
#hist_df = read_historic_floods(flood_hist_path)




############################################################################  SIDEBAR  ############################################################################
with st.form(key="my_form"):



    ce, c1, ce, c2, c3 = st.columns([0.07, 1, 0.07, 5, 0.07])
    with c1:
        info = st.write("Use the widgets to alter the map:")

        select_maps = st.selectbox(
        "What data do you want to see?",
        ("OpenStreetMap", "Stamen Terrain","Stamen Toner"),help="You can choose the number of map style to display",
    )
        input_address = st.text_input("Enter Asset Location", key="Address",value='London, UK',help="You can choose any location in England. Just by typing the name or the area code.",)
        lat,long = center(input_address) #Got the lat & lon
        #history = st.checkbox('See Historic Floods?')

        with st.expander("ℹ️ - About this app", expanded=True):

            st.write(
                """ Map displays flood risk araising from two main sources:
             
1. Rivers & Sea
2. Surface Water"""
            )
            

############################################################################  INTIALIZE MAP  ############################################################################
    with c2:
        map_sby = folium.Map(tiles=select_maps, location=[lat, long], zoom_start=10)

        make_map_responsive= """
        <style>
        [title~="st.iframe"] { width: 100%}
        </style>
        """
        st.markdown(make_map_responsive, unsafe_allow_html=True)

############################################################################  ADDING POLYGON TO MAP  ############################################################################
        #render_asset(input_address,map_sby,c2)
        #add_polygon(gdf,map_sby)
        add_layer(
                    gdf,
                    map_sby,
                    pop_name = 'fra_name',
                    layer_name = 'Risk Area',
                    color = 'orange',
                    centroids = True,show = True)
        
        render_asset(input_address,map_sby,c2)
    submit_button = st.form_submit_button(label="✨ Launch!")

if not submit_button:
    st.stop()


############################################################################  CALCULATE RISK FROM POLYGON  ############################################################################

gdf_out = calculate_risk(gdf,input_address)
st.table(gdf_out.head(5).reset_index(drop=True))

