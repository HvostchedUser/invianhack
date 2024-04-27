from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated, NewType

from annotated_types import Ge, Le
from pydantic import BaseModel, Field

UTMCoordinate = Annotated[float, Ge(0)]
GlobalCoordinate = Annotated[float, Ge(-180), Le(180)]
VehicleID = NewType("VehicleID", int)


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


class TrafficMessage(BaseModel):
    unix_millis: datetime
    center: tuple[UTMCoordinate, UTMCoordinate]
    class_: VehicleType = Field(alias="class")


class TrackedPosition(BaseModel):
    timestamp: datetime
    lat: GlobalCoordinate
    lon: GlobalCoordinate


class TrackedVehicle(BaseModel):
    vehicle_id: VehicleID
    vehicle_class: VehicleType
    vehicle_path: list[TrackedPosition]
    status: TrackedVehicleStatus
