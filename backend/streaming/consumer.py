
import json

from confluent_kafka import Consumer, KafkaException


consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "votestream-consumer-group",
    "auto.offset.reset": "earliest",
})

consumer.subscribe(["votes"])

print("Kafka consumer started. Waiting for vote events...")

try:
    while True:
        message = consumer.poll(timeout=1.0)

        if message is None:
            continue

        if message.error():
            raise KafkaException(message.error())

        event = json.loads(message.value().decode("utf-8"))

        print("Vote event received:")
        print(json.dumps(event, indent=4))

except KeyboardInterrupt:
    print("\nConsumer stopped.")

finally:
    consumer.close()
