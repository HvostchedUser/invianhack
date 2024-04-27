from confluent_kafka import Consumer, KafkaError
import json

# Configuration for Kafka Consumer
kafka_config = {
    "bootstrap.servers": "hack.invian.ru:9094",
    "group.id": "yem22",  # replace 'your_team_id' with your actual team ID
    "auto.offset.reset": "earliest",
}
# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(["aboba"])  # Topic name as provided

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            print("got nothing...")
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue  # End of partition event
            else:
                print(msg.error())
                break
        # Convert the message from Kafka to a Python dictionary
        data = json.loads(msg.value().decode("utf-8"))

        # Convert the dictionary back to a JSON string to print it
        json_data = json.dumps(data, indent=4)
        print(f"Received JSON data: {json_data}")

        # Insert data into MongoDB
        # traffic_data.insert_one(data)

except KeyboardInterrupt:
    print("Stopped by the user.")

finally:
    # Close the consumer and MongoDB connection
    consumer.close()
