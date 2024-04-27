import logging

from confluent_kafka import Consumer, KafkaError
import json
from yem.vehicle_tracker import VehicleTracker
from yem import models
from yem.settings.mongo import mongo_settings
from yem.settings.kafka import kafka_settings

tracker = VehicleTracker(
    mongo_uri=mongo_settings.uri, database_name=mongo_settings.db_name
)

# Configuration for Kafka Consumer
kafka_config = kafka_settings.get_config()

# Create Kafka consumer
consumer = Consumer(kafka_config)
consumer.subscribe(["aboba"])

if __name__ == "__main__":
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    try:
        while True:
            msg = consumer.poll(timeout=1)
            if msg is None:
                logging.warning("Got no message from Kafka")
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    logging.error(msg.error())
                    continue  # End of partition event
                else:
                    logging.error(msg.error())
                    break

            data = models.TrafficMessage(**json.loads(msg.value().decode("utf-8")))
            tracker.add_message(data)

    except KeyboardInterrupt:
        logging.info("Stopped by the user.")

    finally:
        consumer.close()
