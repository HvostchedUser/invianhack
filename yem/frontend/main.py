import time

import folium
import streamlit as st
from streamlit_folium import st_folium

from yem.models import UTMPosition

pos = UTMPosition(easting=389884.6097074643, northing=6184918.59105394)

data = [pos.to_global_position()]

data = [(p.lat, p.lon) for p in data]

st.sidebar.image("./static/logo.svg")
with st.container(border=True):
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

ZOOM = 0.001

st.header(f"Aboba {time.time()}")
# st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

earth_map = folium.Map()

fg = folium.FeatureGroup(name="Autobots")

earth_map.fit_bounds(
    [(data[0][0] - ZOOM, data[0][1] - ZOOM), (data[0][0] + ZOOM, data[0][1] + ZOOM)]
)

for coords in data:
    fg.add_child(folium.CircleMarker(coords, radius=3))

st_folium(earth_map, feature_group_to_add=fg, height=700, width=700)

if "sleep_time" not in st.session_state:
    st.session_state.sleep_time = 2

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

auto_refresh = st.sidebar.checkbox("Auto Refresh?", st.session_state.auto_refresh)

if auto_refresh:
    number = st.sidebar.number_input(
        "Refresh rate in seconds", value=st.session_state.sleep_time
    )
    st.session_state.sleep_time = number
    time.sleep(number)
    st.rerun()

# st.write(styler)
