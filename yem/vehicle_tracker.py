import math
from datetime import datetime

from pydantic import MongoDsn
from pymongo.collection import Collection
import pymongo

from yem import models


class VehicleTracker:
    def __init__(
        self,
        mongo_uri: str | MongoDsn = "mongodb://localhost:27017/",
        database_name: str = "vehicle_tracking",
        max_distance=2,
        max_distance_new=5,
        max_time_gap=0.2,
        inactive_time_threshold=0.5,
    ):
        self.client = pymongo.MongoClient(str(mongo_uri))
        self.db = self.client[database_name]
        self.active_vehicles: Collection = self.db["active_vehicles"]
        self.passed_vehicles: Collection = self.db["passed_vehicles"]
        self.vehicle_id_counter = self.get_next_vehicle_id()
        self.max_distance = max_distance
        self.max_distance_new = max_distance_new
        self.max_time_gap = max_time_gap
        self.inactive_time_threshold = inactive_time_threshold

    def get_next_vehicle_id(self):
        """Retrieve the next available vehicle ID from the database."""
        max_id = self.active_vehicles.find_one(
            sort=[("vehicle_id", -1)], projection={"vehicle_id": 1}
        )
        if max_id is None:
            return 1
        else:
            return max_id["vehicle_id"] + 1

    @staticmethod
    def extrapolate_position(
        pos1: models.UTMPosition,
        pos2: models.UTMPosition,
        time1: datetime,
        time2: datetime,
        target_time: datetime,
    ) -> models.UTMPosition:
        """Extrapolate the position at target_time given two positions and their times."""
        if time1 == time2:
            return pos1  # Avoid division by zero if times are the same
        ratio = (target_time - time1).total_seconds() / (time2 - time1).total_seconds()
        new_y = pos1.northing + (pos2.northing - pos1.northing) * ratio
        new_x = pos1.easting + (pos2.easting - pos1.easting) * ratio
        return models.UTMPosition(northing=new_y, easting=new_x)

    def add_message(self, data: models.TrafficMessage) -> None:
        timestamp = data.timestamp.replace(tzinfo=None)
        class_id = data.class_
        best_id = None
        min_time_distance = float("inf")

        # Modify vehicle data handling to use MongoDB queries
        for vehicle_record in self.active_vehicles.find():
            vehicle_data = models.TrackedVehicle(**vehicle_record)
            vehicle_id = vehicle_data.vehicle_id
            if (
                timestamp - vehicle_data.last_update_time
            ).total_seconds() > self.inactive_time_threshold:
                self._move_to_passed(vehicle_data)
                continue

            for i, entry in enumerate(vehicle_data.vehicle_path):
                time_diff = abs((entry.timestamp - timestamp).total_seconds())
                if time_diff < self.max_time_gap:
                    if i > 0:
                        max_distance = self.max_distance
                        prev_entry = vehicle_data.vehicle_path[i - 1]
                        extrapolated_pos = self.extrapolate_position(
                            prev_entry.position,
                            entry.position,
                            prev_entry.timestamp,
                            entry.timestamp,
                            timestamp,
                        )
                    else:
                        extrapolated_pos = entry.position
                        max_distance = self.max_distance_new

                    dist = math.dist(extrapolated_pos, data.position)
                    if time_diff < min_time_distance and dist < max_distance:
                        min_time_distance = dist
                        best_id = vehicle_id

        # Create new vehicle record if no suitable track is found
        if best_id is None:
            best_id = self.vehicle_id_counter
            self.active_vehicles.insert_one(
                {
                    "vehicle_id": best_id,
                    "vehicle_class": class_id,
                    "vehicle_path": [],
                    "status": models.TrackedVehicleStatus.ACTIVE,
                }
            )
            self.vehicle_id_counter += 1

        # Append new position to the path of the identified vehicle
        self.active_vehicles.update_one(
            {"vehicle_id": best_id},
            {
                "$push": {
                    "vehicle_path": {"timestamp": timestamp, "position": data.position}
                }
            },
        )

    def get_vehicle_data(
        self, min_path_points=5, return_passed: bool = False
    ) -> list[models.TrackedVehicle]:
        result = []
        for vehicle_record in self.active_vehicles.find():
            vehicle_data = models.TrackedVehicle(**vehicle_record)
            if (
                datetime.utcnow() - vehicle_data.last_update_time
            ).total_seconds() > self.inactive_time_threshold * 3:
                self._move_to_passed(vehicle_data)
                continue
            if len(vehicle_data.vehicle_path) > min_path_points:
                result.append(vehicle_data)
        if return_passed:
            for vehicle_data in self.passed_vehicles.find():
                if len(vehicle_data["vehicle_path"]) > min_path_points:
                    result.append(models.TrackedVehicle(**vehicle_data))
        return result

    def _move_to_passed(self, vehicle_data: models.TrackedVehicle) -> None:
        with self.client.start_session() as session:
            with session.start_transaction():
                self.passed_vehicles.insert_one(vehicle_data.model_dump())
                self.active_vehicles.delete_one({"vehicle_id": vehicle_data.vehicle_id})
