from confluent_kafka import Consumer, KafkaError
import json
import matplotlib.pyplot as plt
import numpy as np
import math

# Configuration for Kafka Consumer
kafka_config = {
    'bootstrap.servers': 'hack.invian.ru:9094',
    'group.id': 'yem',
    'auto.offset.reset': 'earliest'
}

# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(['aboba'])

# Function to calculate distance between two points
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

# Initialize plot
plt.ion()
fig, ax = plt.subplots()

central_x = 6184907.837245346+30
central_y = 389832.830408114+30
xlim = (central_x-30, central_x+30)
ylim = (central_y-30, central_y+30)
ax.set_xlim(xlim)
ax.set_ylim(ylim)
ax.set_title('Real-Time UTM Coordinates Visualization')
ax.set_xlabel('Easting (m)')
ax.set_ylabel('Northing (m)')

# Vehicle tracking data
vehicles_detected = {}
vehicle_id_counter = 0
distance_threshold = 3.0  # Threshold to consider a point the same vehicle
color_map = plt.cm.get_cmap('hsv', 10)  # Colormap for up to 10 vehicles, can increase as needed
quiver = None

def update_plot():
    global quiver
    if quiver:
        quiver.remove()
    X, Y, U, V, colors = [], [], [], [], []
    print(len(vehicles_detected.items()))
    for vehicle_id, (pos, prev_pos) in vehicles_detected.items():
        x, y = pos
        px, py = prev_pos
        X.append(x)
        Y.append(y)
        U.append(x - px)
        V.append(y - py)
        colors.append(color_map(vehicle_id % 30))  # Use vehicle ID to assign color
    quiver = ax.quiver(X, Y, U, V, color=colors, angles='xy', scale_units='xy', scale=1)
    plt.draw()
    plt.pause(0.01)
try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("none...")
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break
        data = json.loads(msg.value().decode('utf-8'))
        coord = data.get("center")
        x, y = coord[0], coord[1]
        new_point = (x, y)
        found = False
        for vehicle_id, (pos, prev_pos) in list(vehicles_detected.items()):
            if calculate_distance(pos, new_point) < distance_threshold:
                vehicles_detected[vehicle_id] = (new_point, pos)
                found = True
                break
        if not found:
            vehicles_detected[vehicle_id_counter] = (new_point, new_point)  # Initialize with same position for start
            vehicle_id_counter += 1
        update_plot()

except KeyboardInterrupt:
    print("Stopped by the user.")

finally:
    consumer.close()
    plt.ioff()
    plt.show()
