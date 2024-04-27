from confluent_kafka import Consumer, KafkaError
import json
import matplotlib.pyplot as plt
import numpy as np

import cartopy.crs as ccrs
import cartopy.io.img_tiles as cimgt


request = cimgt.OSM()
projection = ccrs.UTM(39)  # For Kazan

# Configuration for Kafka Consumer
kafka_config = {
    'bootstrap.servers': 'hack.invian.ru:9094',
    'group.id': 'yem1',
    'auto.offset.reset': 'earliest'
}

# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(['aboba'])

# Initial coordinates and plot setup
central_y = 6184907.837245346+30
central_x = 389832.830408114+30
xlim = (central_x - 30, central_x + 30)  # 1000 meter buffer around the central point
ylim = (central_y - 30, central_y + 30)

plt.ion()  # Turn the interactive mode on for real-time updates
fig, ax = plt.subplots(subplot_kw={'projection': request.crs})
ax.set_extent([xlim[0], xlim[1], ylim[0], ylim[1]], crs=projection)
sc = ax.scatter([], [], c='blue', transform=projection)  # Initialize an empty scatter plot
ax.set_title('Real-Time UTM Coordinates Visualization')
ax.set_xlabel('Easting (m)')
ax.set_ylabel('Northing (m)')
ax.add_image(request, 18)

def update_plot(x, y):
    sc.set_offsets(np.c_[x, y])
    plt.draw()
    plt.pause(0.01)

try:
    x_data, y_data = [], []
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("none...")
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue  # End of partition event
            else:
                print(msg.error())
                break
        data = json.loads(msg.value().decode('utf-8'))
        coord = data.get("center")
        x, y = coord[1], coord[0]
        print(x,y)
        x_data.append(x)
        y_data.append(y)
        update_plot(x_data, y_data)
        # break

except KeyboardInterrupt:
    print("Stopped by the user.")

finally:
    consumer.close()
    plt.ioff()  # Turn off interactive plotting
    plt.show()  # Ensure window stays open after the loop ends
