import math
from datetime import datetime

from yem import models


class VehicleTracker:
    def __init__(
        self,
        max_distance=2,
        max_distance_new=5,
        max_time_gap=0.2,
        inactive_time_threshold=0.5,
    ):
        self.active_vehicles: dict[models.VehicleID, models.TrackedVehicle] = {}
        self.passed_vehicles: dict[models.VehicleID, models.TrackedVehicle] = {}
        self.vehicle_id_counter = 1
        self.max_distance = max_distance
        self.max_distance_new = max_distance_new
        self.max_time_gap = max_time_gap
        self.inactive_time_threshold = inactive_time_threshold

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
        ratio = (target_time - time1).seconds / (time2 - time1).seconds
        new_y = pos1.northing + (pos2.northing - pos1.northing) * ratio
        new_x = pos1.easting + (pos2.easting - pos1.easting) * ratio
        return models.UTMPosition(northing=new_y, easting=new_x)

    def add_message(self, data: models.TrafficMessage) -> None:
        timestamp = data.timestamp
        class_id = data.class_

        best_id = None
        min_time_distance = float("inf")

        # Check both active and passed vehicles for potential updates
        for vehicle_id, vehicle_data in self.active_vehicles.copy().items():
            last_update_time = vehicle_data.vehicle_path[-1].timestamp
            if (timestamp - last_update_time).seconds > self.inactive_time_threshold:
                if vehicle_id in self.active_vehicles:
                    self.passed_vehicles[vehicle_id] = self.active_vehicles.pop(
                        vehicle_id
                    )
                    self.passed_vehicles[
                        vehicle_id
                    ].status = models.TrackedVehicleStatus.PASSED
                continue

            for i, entry in enumerate(vehicle_data.vehicle_path):
                time_diff = abs((entry.timestamp - timestamp).seconds)
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
            best_id = models.VehicleID(self.vehicle_id_counter)
            self.active_vehicles[best_id] = models.TrackedVehicle(
                vehicle_id=best_id,
                vehicle_class=class_id,
                vehicle_path=[],
                status=models.TrackedVehicleStatus.ACTIVE,
            )
            self.vehicle_id_counter += 1

        # Append new position to the path of the identified vehicle
        self.active_vehicles[best_id].vehicle_path.append(
            models.TrackedPosition(timestamp=timestamp, position=data.position)
        )

    def get_vehicle_data(self, min_path_points=5) -> list[models.TrackedVehicle]:
        result = []
        # Output for both active and passed vehicles
        for vehicle_dict in [self.active_vehicles, self.passed_vehicles]:
            for vehicle_id, vehicle_data in vehicle_dict.items():
                if len(vehicle_data.vehicle_path) > min_path_points:
                    result.append(vehicle_data)
        return result
