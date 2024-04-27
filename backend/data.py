from enum import IntEnum
from typing import Annotated

from annotated_types import Ge
from pydantic import BaseModel, Field

UTMCoordinate = Annotated[float, Ge(0)]


class VehicleType(IntEnum):
    MOTORCYCLE = 0
    CAR = 1
    CAR_WITH_TRAILER = 2
    TRUCK = 3
    ROAD_TRAIN = 4
    BUS = 5


class TrafficMessage(BaseModel):
    unix_millis: ...
    center: tuple[UTMCoordinate, UTMCoordinate]
    class_: ... = Field(alias="class")
