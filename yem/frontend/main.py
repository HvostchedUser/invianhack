import time

import folium
import streamlit as st
from folium import Icon
from streamlit_folium import st_folium

from yem.consumer import tracker
from yem.models import UTMPosition, TrackedVehicle, VEHICLE_TYPE_TO_ICON

start_pos = UTMPosition(easting=389860, northing=6184940)

vehicles = tracker.get_vehicle_data(prune_old=True, return_passed=False)

data = [
    v
    for v in vehicles
    # if v.status == TrackedVehicleStatus.ACTIVE
]

st.sidebar.image("./static/logo.svg")
with st.container(border=True):
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

ZOOM = 0.001

st.header(f"Aboba {time.time()}")
# st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

earth_map = folium.Map()

fg = folium.FeatureGroup(name="Autobots")

# ROOT_VIEW = (55.79728057677817, 49.24356827846827)
ROOT_VIEW = start_pos.to_global_position()

earth_map.fit_bounds(
    [
        (ROOT_VIEW[0] - ZOOM, ROOT_VIEW[1] - ZOOM),
        (ROOT_VIEW[0] + ZOOM, ROOT_VIEW[1] + ZOOM),
    ]
)


def draw_icon(v: TrackedVehicle, loc, paths_to_draw: int = 30):
    icon = VEHICLE_TYPE_TO_ICON[v.vehicle_class]
    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
        "cadetblue",
        "darkpurple",
        "pink",
        "lightgreen",
        "gray",
        "black",
        "lightgray",
    ]
    color = colors[v.vehicle_id % len(colors)]
    for i, path in enumerate(v.vehicle_path[-paths_to_draw:-1]):
        opacity = float(i) / paths_to_draw
        opacity = max(0.1, opacity)
        opacity = min(1.0, opacity)

        radius = (float(i) / float(paths_to_draw)) * 5
        radius = max(1.0, radius)

        fg.add_child(
            folium.CircleMarker(
                location=path.position.to_global_position(),
                color=color,
                radius=radius,
                opacity=0,
                fill=True,
                fill_color=color,
                fill_opacity=opacity / 2,
            )
        )
    fg.add_child(folium.Marker(loc, icon=Icon(icon=icon, prefix="fa", color=color)))


for vehicle in data:
    coord = vehicle.vehicle_path[-1].position.to_global_position()
    draw_icon(vehicle, coord)

st_folium(earth_map, feature_group_to_add=fg, height=700, width=700)

if "sleep_time" not in st.session_state:
    st.session_state.sleep_time = 0.3

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
