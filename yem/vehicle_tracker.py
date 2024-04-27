import json
import math

class VehicleTracker:
    def __init__(self, max_distance=2, max_distance_new=5, max_time_gap=200, inactive_time_threshold=500):
        self.active_vehicles = {}
        self.passed_vehicles = {}
        self.vehicle_id_counter = 1
        self.max_distance = max_distance
        self.max_distance_new = max_distance_new
        self.max_time_gap = max_time_gap
        self.inactive_time_threshold = inactive_time_threshold

    def distance(self, pos1, pos2):
        """ Calculate Euclidean distance between two points. """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def extrapolate_position(self, pos1, pos2, time1, time2, target_time):
        """ Extrapolate the position at target_time given two positions and their times. """
        if time1 == time2:
            return pos1  # Avoid division by zero if times are the same
        ratio = (target_time - time1) / (time2 - time1)
        new_x = pos1[0] + (pos2[0] - pos1[0]) * ratio
        new_y = pos1[1] + (pos2[1] - pos1[1]) * ratio
        return [new_x, new_y]

    def add_message(self, data):
        unix_millis = data['unix_millis']
        center = data['center']
        class_id = data['class']

        best_id = None
        min_time_distance = float('inf')

        # Check both active and passed vehicles for potential updates
        for vehicle_dict in [self.active_vehicles.copy()]:
            for vehicle_id, vehicle_data in vehicle_dict.items():
                last_update_time = vehicle_data['path'][-1]['unix_millis']
                if unix_millis - last_update_time > self.inactive_time_threshold:
                    if vehicle_id in self.active_vehicles:
                        self.passed_vehicles[vehicle_id] = self.active_vehicles.pop(vehicle_id)
                        self.passed_vehicles[vehicle_id]['passed'] = True
                    continue

                for i in range(len(vehicle_data['path'])):
                    entry = vehicle_data['path'][i]
                    time_diff = abs(entry['unix_millis'] - unix_millis)
                    if time_diff < self.max_time_gap:
                        if i > 0:
                            max_distance = self.max_distance
                            prev_entry = vehicle_data['path'][i-1]
                            extrapolated_pos = self.extrapolate_position(
                                prev_entry['center'], entry['center'],
                                prev_entry['unix_millis'], entry['unix_millis'], unix_millis
                            )
                        else:
                            extrapolated_pos = entry['center']
                            max_distance = self.max_distance_new

                        dist = self.distance(extrapolated_pos, center)
                        if time_diff < min_time_distance and dist < max_distance:
                            min_time_distance = dist
                            best_id = vehicle_id

        # Create new vehicle record if no suitable track is found
        if best_id is None:
            best_id = self.vehicle_id_counter
            self.active_vehicles[best_id] = {'class': class_id, 'path': [], 'passed': False}
            self.vehicle_id_counter += 1

        # Append new position to the path of the identified vehicle
        self.active_vehicles[best_id]['path'].append({
            'unix_millis': unix_millis,
            'center': center
        })


    def get_vehicle_data(self, min_path_points=5):
        result = []
        # Output for both active and passed vehicles
        for vehicle_dict, status in [(self.active_vehicles, "active"), (self.passed_vehicles, "passed")]:
            for vehicle_id, vehicle_data in vehicle_dict.items():
                if len(vehicle_data['path']) > min_path_points:
                    vehicle_output = {
                        'vehicle_id': vehicle_id,
                        'vehicle_class': vehicle_data['class'],
                        'vehicle_path': vehicle_data['path'],
                        'status': status
                    }
                    result.append(json.dumps(vehicle_output))
        return result
