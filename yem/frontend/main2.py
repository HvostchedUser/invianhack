from datetime import datetime, time, timedelta, date
from time import sleep

import folium
import streamlit as st
from folium import Icon
from streamlit_folium import st_folium

from yem.consumer import tracker
from yem.models import (
    UTMPosition,
    TrackedVehicle,
    VEHICLE_TYPE_TO_ICON,
    VehicleType,
    GlobalPosition,
)

start_pos = UTMPosition(easting=389865, northing=6184940)

vehicles = tracker.get_vehicle_data()


def draw_sidebar():
    st.sidebar.image("./static/logo.png")
    st.sidebar.text(" ")

    c1, c2 = st.sidebar.columns(2)
    t: time = c1.time_input("From", value=time(0, 15))
    dt: timedelta = datetime.combine(date.min, t) - datetime.min
    # c2.time_input("To")

    car_types = st.sidebar.multiselect("Choose Car types:", VehicleType.list())
    if not car_types:
        car_types = VehicleType.list()

    return set(map(VehicleType.from_beautiful, car_types))


def append_diff(loc):
    dx, dy = 0.00004, 0.000
    return GlobalPosition(loc[0] + dx, loc[1] + dy)


def draw_vehicle(
    fg: folium.FeatureGroup,
    v: TrackedVehicle,
    paths_to_draw: int = 10,
    skip_each_path: int = 3,
):
    loc = v.sorted_vehicle_path[-1].position.to_global_position()
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
    for i, path in list(enumerate(v.sorted_vehicle_path[::skip_each_path]))[
        -paths_to_draw:
    ]:
        # opacity = float(i) / paths_to_draw
        # opacity = max(0.1, opacity)
        # opacity = min(1.0, opacity)
        #
        # radius = (float(i) / float(paths_to_draw)) * 5
        # radius = max(1.0, radius)

        coord = path.position.to_global_position()
        line_coords.append(append_diff(coord))
        # fg.add_child(
        #     folium.CircleMarker(
        #         location=path.position.to_global_position(),
        #         color=color,
        #         radius=radius,
        #         opacity=0,
        #         fill=True,
        #         fill_color=color,
        #         fill_opacity=opacity / 2,
        #     )
        # )
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


def draw_speeds(fg: folium.FeatureGroup):
    LANE_POINTS = {
        UTMPosition(northing=6184960.5, easting=389909): "east",
        UTMPosition(northing=6184919, easting=389821): "west",
        UTMPosition(northing=6184908, easting=389885): "south",
    }

    for coord, name in LANE_POINTS.items():
        fg.add_child(folium.CircleMarker(coord.to_global_position()))


def refresh(show=False):
    if "sleep_time" not in st.session_state:
        st.session_state.sleep_time = 0.3

    if "auto_refresh" not in st.session_state:
        st.session_state.auto_refresh = True

    if show:
        auto_refresh = st.sidebar.checkbox(
            "Auto Refresh?", st.session_state.auto_refresh
        )
    else:
        auto_refresh = st.session_state.auto_refresh

    if auto_refresh:
        if show:
            number = st.sidebar.number_input(
                "Refresh rate in seconds", value=st.session_state.sleep_time
            )
        else:
            number = st.session_state.sleep_time = 0.3

        sleep(number)
        st.rerun()


def draw_map(zoom=0.0005) -> folium.Map:
    earth_map = folium.Map()

    ROOT_VIEW = start_pos.to_global_position()

    earth_map.fit_bounds(
        [
            (ROOT_VIEW[0] - zoom, ROOT_VIEW[1] - zoom),
            (ROOT_VIEW[0] + zoom, ROOT_VIEW[1] + zoom),
        ]
    )

    return earth_map


def draw():
    with st.container(border=True):
        st.image("https://upload.wikimedia.org/wikipedia/commons/f/fd/ABOBA.jpg")

    car_types = draw_sidebar()

    fg = folium.FeatureGroup(name="Vehicles", show=False)
    for vehicle in vehicles:
        if vehicle.vehicle_class in car_types:
            draw_vehicle(fg, vehicle)

    earth_map = draw_map()
    draw_speeds(fg)
    st_folium(earth_map, feature_group_to_add=fg, height=700, width=700)
    refresh()


if __name__ == "__main__":
    draw()
