import math
from collections import defaultdict
from datetime import datetime
from enum import IntEnum, StrEnum
from types import MappingProxyType
from typing import Annotated, NewType, NamedTuple

from annotated_types import Ge, Le
from pydantic import BaseModel, Field

UTMCoordinate = Annotated[float, Ge(0)]
VehicleID = NewType("VehicleID", int)


class GlobalPosition(NamedTuple):
    lat: Annotated[float, Ge(-90), Le(90)]
    lon: Annotated[float, Ge(-180), Le(180)]


class UTMPosition(NamedTuple):
    northing: UTMCoordinate
    easting: UTMCoordinate

    def to_global_position(
        self, zone: int = 39, northern_hemisphere=True
    ) -> GlobalPosition:
        """Source: https://stackoverflow.com/a/344083"""
        northing = self.northing
        easting = self.easting
        if not northern_hemisphere:
            northing = 10000000 - northing

        a = 6378137
        e = 0.081819191
        e1sq = 0.006739497
        k0 = 0.9996

        arc = northing / k0
        mu = arc / (
            a
            * (
                1
                - math.pow(e, 2) / 4.0
                - 3 * math.pow(e, 4) / 64.0
                - 5 * math.pow(e, 6) / 256.0
            )
        )

        ei = (1 - math.pow((1 - e * e), (1 / 2.0))) / (
            1 + math.pow((1 - e * e), (1 / 2.0))
        )

        ca = 3 * ei / 2 - 27 * math.pow(ei, 3) / 32.0

        cb = 21 * math.pow(ei, 2) / 16 - 55 * math.pow(ei, 4) / 32
        cc = 151 * math.pow(ei, 3) / 96
        cd = 1097 * math.pow(ei, 4) / 512
        phi1 = (
            mu
            + ca * math.sin(2 * mu)
            + cb * math.sin(4 * mu)
            + cc * math.sin(6 * mu)
            + cd * math.sin(8 * mu)
        )

        n0 = a / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (1 / 2.0))

        r0 = (
            a
            * (1 - e * e)
            / math.pow((1 - math.pow((e * math.sin(phi1)), 2)), (3 / 2.0))
        )
        fact1 = n0 * math.tan(phi1) / r0

        _a1 = 500000 - easting
        dd0 = _a1 / (n0 * k0)
        fact2 = dd0 * dd0 / 2

        t0 = math.pow(math.tan(phi1), 2)
        Q0 = e1sq * math.pow(math.cos(phi1), 2)
        fact3 = (5 + 3 * t0 + 10 * Q0 - 4 * Q0 * Q0 - 9 * e1sq) * math.pow(dd0, 4) / 24

        fact4 = (
            (61 + 90 * t0 + 298 * Q0 + 45 * t0 * t0 - 252 * e1sq - 3 * Q0 * Q0)
            * math.pow(dd0, 6)
            / 720
        )

        lof1 = _a1 / (n0 * k0)
        lof2 = (1 + 2 * t0 + Q0) * math.pow(dd0, 3) / 6.0
        lof3 = (
            (
                5
                - 2 * Q0
                + 28 * t0
                - 3 * math.pow(Q0, 2)
                + 8 * e1sq
                + 24 * math.pow(t0, 2)
            )
            * math.pow(dd0, 5)
            / 120
        )
        _a2 = (lof1 - lof2 + lof3) / math.cos(phi1)
        _a3 = _a2 * 180 / math.pi

        latitude = 180 * (phi1 - fact1 * (fact2 + fact3 + fact4)) / math.pi

        if not northern_hemisphere:
            latitude = -latitude

        longitude = ((zone > 0) and (6 * zone - 183.0) or 3.0) - _a3
        return GlobalPosition(lat=latitude, lon=longitude)


class TrackedVehicleStatus(StrEnum):
    ACTIVE = "active"
    PASSED = "passed"


class VehicleType(IntEnum):
    MOTORCYCLE = 0
    CAR = 1
    CAR_WITH_TRAILER = 2
    TRUCK = 3
    ROAD_TRAIN = 4
    BUS = 5


VEHICLE_TYPE_TO_ICON = MappingProxyType(
    {
        VehicleType.MOTORCYCLE: "motorcycle",
        VehicleType.CAR: "car",
        VehicleType.CAR_WITH_TRAILER: "trailer",
        VehicleType.TRUCK: "truck",
        VehicleType.ROAD_TRAIN: "truck-moving",
        VehicleType.BUS: "bus",
    }
)


class TrafficMessage(BaseModel):
    timestamp: datetime = Field(alias="unix_millis")
    position: UTMPosition = Field(alias="center")
    class_: VehicleType = Field(alias="class")


class TrackedPosition(BaseModel):
    timestamp: datetime
    position: UTMPosition


class JunctionInputLane(StrEnum):
    EAST = "east"
    WEST = "west"
    SOUTH = "south"


class JunctionOutputLane(StrEnum):
    EAST = "east"
    WEST = "west"
    SOUTH = "south"


LANE_POINTS = {
    UTMPosition(northing=6184968.86, easting=389909.58): "east",
    UTMPosition(northing=6184928.33, easting=389821.43): "west",
    UTMPosition(northing=6184908.56, easting=389885.40): "south",
}


def nearest_lane(position: UTMPosition) -> str:
    return LANE_POINTS[min(LANE_POINTS, key=lambda x: math.dist(x, position))]


class TrackedVehicle(BaseModel):
    vehicle_id: VehicleID
    vehicle_class: VehicleType
    vehicle_path: list[TrackedPosition]
    status: TrackedVehicleStatus
    input_lane: JunctionInputLane | None = None
    output_lane: JunctionOutputLane | None = None

    @property
    def last_update_time(self) -> datetime | None:
        return self.sorted_vehicle_path[-1].timestamp if self.vehicle_path else None

    @property
    def sorted_vehicle_path(self) -> list[TrackedPosition]:
        return sorted(self.vehicle_path, key=lambda p: p.timestamp)

    def aggregate_speed(self, use_last_n_points: int = 10) -> float:
        """Return average speed in km/h"""
        if not self.vehicle_path:
            return 0
        speeds = []
        sorted_path = self.sorted_vehicle_path
        for prev_p, next_p in zip(
            sorted_path[-use_last_n_points - 1 : -1], sorted_path[-use_last_n_points:]
        ):
            dist = math.dist(prev_p.position, next_p.position)
            time = (next_p.timestamp - prev_p.timestamp).total_seconds()
            speeds.append(dist / time if time > 0 else 0)
        if not speeds:
            return 0
        return sum(speeds) / len(speeds) * 3.6


class LaneStats(BaseModel):
    vehicle_count: defaultdict[VehicleType, int] = defaultdict(int)
    average_speed: defaultdict[VehicleType, float] = defaultdict(float)
