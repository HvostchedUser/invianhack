from datetime import datetime, time, timedelta, date
from time import sleep

import folium
import streamlit as st
from folium import Icon
from streamlit_folium import st_folium

from yem.consumer import tracker
from yem.frontend.vis_utils import make_bar_chart, TYPE_COLORS
from yem.models import (
    UTMPosition,
    TrackedVehicle,
    VEHICLE_TYPE_TO_ICON,
    VehicleType,
    GlobalPosition,
    JunctionOutputLane,
)

start_pos = UTMPosition(easting=389865, northing=6184940)

vehicles = tracker.get_vehicle_data()


def draw_sidebar():
    st.sidebar.image("./static/logo.png")
    st.sidebar.text(" ")

    t: time = st.sidebar.time_input("Statistics Timespan", value=time(0, 15))
    dt: timedelta = datetime.combine(date.min, t) - datetime.min

    car_types = st.sidebar.multiselect("Choose Car types:", VehicleType.list())
    if not car_types:
        car_types = VehicleType.list()
    return set(map(VehicleType.from_beautiful, car_types)), dt


car_types, dt = draw_sidebar()
with st.container(border=True):
    st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

ZOOM = 0.0005

earth_map = folium.Map()

fg = folium.FeatureGroup(name="Autobots", show=False)

ROOT_VIEW = start_pos.to_global_position()

earth_map.fit_bounds(
    [
        (ROOT_VIEW[0] - ZOOM, ROOT_VIEW[1] - ZOOM),
        (ROOT_VIEW[0] + ZOOM, ROOT_VIEW[1] + ZOOM),
    ]
)


def draw_lane_stats():
    stats = tracker.get_lane_stats(dt, list(car_types))

    LANE_POINTS = {
        UTMPosition(
            northing=6184960.5, easting=389909
        ).to_global_position(): JunctionOutputLane.EAST,
        UTMPosition(
            northing=6184919, easting=389821
        ).to_global_position(): JunctionOutputLane.WEST,
        UTMPosition(
            northing=6184908, easting=389885
        ).to_global_position(): JunctionOutputLane.SOUTH,
    }

    for coord, lane in LANE_POINTS.items():
        lane_stats = stats[lane]

        average_speed = sum(lane_stats.average_speed[t] for t in car_types)

        fg.add_child(
            folium.Marker(
                coord,
                icon=folium.DivIcon(
                    icon_size=(100, 50), html=f"<h3>{average_speed:.1f} km/h</h3>"
                ),
            )
        )

        for rect in make_bar_chart(
            lane_stats, scale_factor=0.0000005, rotation_angle=90
        ):
            color, *corners = rect

            ld = corners[0], corners[1]
            lu = corners[0], corners[3]
            ru = corners[2], corners[1]
            rd = corners[2], corners[3]

            polycoords = [ld, lu, rd, ru]

            polycoords = [
                (x + coord[0] - 0.0001, y + coord[1] - 0.0004) for x, y in polycoords
            ]

            fg.add_child(
                folium.Polygon(
                    polycoords, fill=True, fill_color=color, opacity=0, fill_opacity=0.5
                )
            )
    for type in TYPE_COLORS:
        c1, c2 = st.sidebar.columns(2)

        color = TYPE_COLORS[type]
        html_string = f"<h3 style='color: {color}'>{color}</h3>"

        c2.markdown(html_string, unsafe_allow_html=True)
        c1.write(type.to_beautiful())


draw_lane_stats()


def append_diff(loc):
    dx, dy = 0.00004, 0.000
    return GlobalPosition(loc[0] + dx, loc[1] + dy)


def draw_icon(v: TrackedVehicle, paths_to_draw: int = 30):
    loc = vehicle.sorted_vehicle_path[-1].position.to_global_position()
    loc = append_diff(loc)
    icon = VEHICLE_TYPE_TO_ICON[v.vehicle_class]
    colors = [
        "blue",
        "green",
        "red",
        "purple",
        "orange",
        "darkblue",
        "darkgreen",
    ]
    color = colors[v.vehicle_id % len(colors)]
    line_coords = [loc]
    for i, path in list(enumerate(v.sorted_vehicle_path[::3]))[-10:]:
        coord = path.position.to_global_position()
        line_coords.append(append_diff(coord))

    if len(line_coords) > 2:
        fg.add_child(
            folium.ColorLine(
                line_coords,
                colors=range(len(line_coords) - 1),
                colormap=[(1, 1, 1, 0), color],
                weight=5,
                opacity=0.5,
            )
        )
    fg.add_child(folium.Marker(loc, icon=Icon(icon=icon, prefix="fa", color=color)))


for vehicle in vehicles:
    if vehicle.vehicle_class in car_types:
        draw_icon(vehicle)

st_folium(earth_map, feature_group_to_add=fg, height=700, width=700)

if "sleep_time" not in st.session_state:
    st.session_state.sleep_time = 0.3

if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True

auto_refresh = st.session_state.auto_refresh

if auto_refresh:
    number = st.session_state.sleep_time
    st.session_state.sleep_time = number
    sleep(st.session_state.sleep_time)
    st.rerun()
