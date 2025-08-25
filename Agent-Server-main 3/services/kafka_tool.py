from confluent_kafka import Producer
import json
import logging
import uuid

class KafkaProducerTool:
    def __init__(self, bootstrap_servers, topic):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.topic = topic

    def delivery_report(self, err, msg):
        if err is not None:
            logging.error(f'Message delivery failed: {err}')
        else:
            logging.info(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def send_message(self, data):
        try:
            self.producer.produce(
                self.topic,
                key=str(uuid.uuid4()),
                value=json.dumps(data),
                on_delivery=self.delivery_report
            )
            self.producer.flush()
        except Exception as e:
            logging.error(f'Error sending message to Kafka: {e}')