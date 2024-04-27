from confluent_kafka import Consumer, KafkaError
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from vehicle_tracker import VehicleTracker
from yem import models

tracker = VehicleTracker()

# Configuration for Kafka Consumer
kafka_config = {
    "bootstrap.servers": "hack.invian.ru:9094",
    "group.id": "yem1",
    "auto.offset.reset": "earliest",
}

# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(["aboba"])

# Initial coordinates and plot setup
central_y = 6184907.837245346 + 30
central_x = 389832.830408114 + 30
xlim = (central_x - 30, central_x + 30)  # 1000 meter buffer around the central point
ylim = (central_y - 30, central_y + 30)

plt.ion()  # Turn the interactive mode on for real-time updates
fig, ax = plt.subplots()
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title("Real-Time UTM Coordinates Visualization")
ax.set_xlabel("Easting (m)")
ax.set_ylabel("Northing (m)")

# Dictionary to store vehicle scatter plot objects
vehicle_plots = {}
color_map = ListedColormap(
    plt.cm.get_cmap("tab20").colors
)  # Using 'tab20' colormap for distinct colors

iterv = 0


def update_plot(vehicle_data: list[models.TrackedVehicle]):
    global iterv
    iterv += 1
    if iterv % 100 != 0:
        return
    for vehicle in vehicle_data:
        vehicle_id = vehicle.vehicle_id
        x, y = [], []
        for point in vehicle.vehicle_path:
            coord = point.position
            x.append(coord.easting)
            y.append(coord.northing)

        # Check if this vehicle already has a scatter plot
        if vehicle_id in vehicle_plots:
            vehicle_plots[vehicle_id].set_offsets(np.c_[x, y])
        else:
            # Create a new scatter plot for the vehicle
            vehicle_plots[vehicle_id] = ax.scatter(
                x, y, c=[color_map(vehicle_id % 20)], label=f"Vehicle {vehicle_id}"
            )
    if vehicle_data:
        plt.legend()
        plt.draw()
        plt.pause(0.1)


try:
    while True:
        msg = consumer.poll(timeout=1)
        if msg is None:
            print("none...")
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(msg.error())
                continue  # End of partition event
            else:
                print(msg.error())
                break

        data = models.TrafficMessage(**json.loads(msg.value().decode("utf-8")))
        tracker.add_message(data)
        vehicle_data = tracker.get_vehicle_data()
        update_plot(vehicle_data)

except KeyboardInterrupt:
    print("Stopped by the user.")

finally:
    consumer.close()
    plt.ioff()  # Turn off interactive plotting
    plt.show()  # Ensure window stays open after the loop ends
