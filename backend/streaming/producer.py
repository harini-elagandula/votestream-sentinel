
import json
import os

from confluent_kafka import Producer


KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS",
    "localhost:9092",
)

producer = Producer({
    "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
})


def delivery_report(err, message):
    if err is not None:
        print(f"Kafka delivery failed: {err}")
    else:
        print(
            f"Kafka event delivered: "
            f"topic={message.topic()}, "
            f"partition={message.partition()}"
        )


def publish_vote_event(event: dict):
    producer.produce(
        topic="votes",
        key=str(event["election_id"]),
        value=json.dumps(event),
        callback=delivery_report,
    )
    producer.poll(0)
    producer.flush(timeout=5)
