from kafka import KafkaConsumer
from kafka import TopicPartition
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.platform import asyncio
import asyncio
import json
import time
import logging
import threading
import collections
from argparse import ArgumentParser

KAFKA_TOPIC = 'pipeline'
KAFKA_BOOTSTRAP_SERVER = 'localhost:9092'
SESSION_STATE_ESTABLISHED = "ESTABLISHED"
TIMEOUT = 60


def validate_bgp_peer(kafka_consumer, node, peer_address,
                      session_state=SESSION_STATE_ESTABLISHED,
                      timeout=TIMEOUT):
    """Validate BGP session state."""
    telemetry_encoding_path = "openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor"
    start_time = time.time()
    for kafka_msg in kafka_consumer:
        msg = json.loads(kafka_msg.value.decode('utf-8'))
        if (msg["Telemetry"]["node_id_str"] == node and
                msg["Telemetry"]["encoding_path"] == telemetry_encoding_path
                and "Rows" in msg):
            for row in msg["Rows"]:
                if ("neighbor-address" in row["Keys"] and
                        row["Keys"]["neighbor-address"] == peer_address and
                        "state" in row["Content"] and
                        "session-state" in row["Content"]["state"] and
                        row["Content"]["state"]["session-state"] == session_state):
                    return True

        if time.time() - start_time > timeout:
            break

    return False


class Consumer(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    # daemon = True

    def __init__(self, kafka_consumer, handler):
        self._consumer = kafka_consumer
        super(Consumer, self).__init__()
        # self._stop_event = threading.Event()
        self.handler = handler

    def run(self):
        for message in self._consumer:
            # message = str(message)
            message_dict = json.loads(message.value.decode("utf-8"))
            logging.info("Got a message!")
            logging.info(json.dumps(message_dict, indent=2, sort_keys=True))
            self.handler.send_message_open_ws(json.dumps(message_dict, indent=2, sort_keys=True))

    def subscribe(self, topic):
        self._consumer.subscribe('pipeline')

    def close(self):
        self._consumer.close()
    def pause(self):
        logging.info("Pausing kafka consumer subscription to pipeline...")
        partitions = list(self._consumer.assignment())
        # partition = partitions[0]
        partition = TopicPartition(topic='pipeline', partition=0)
        self._consumer.pause(partition)
    def resume(self):
        logging.info("Resuming kafka consumer subscription to pipeline...")
        partitions = list(self._consumer.assignment())
        # partition = partitions[0]
        partition = TopicPartition(topic='pipeline', partition=0)
        self._consumer.resume(partition)
    # def stop(self):
    #     logging.info("Halting telemetry thread...")
    #     self._stop_event.set()
    # def stopped(self):
    #     return self._stop_event.is_set()

def init_telemetry(handler):
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    kafka_consumer = Consumer(KafkaConsumer('pipeline'), handler)
    # Start the kafka consumer thread.
    kafka_consumer.start()
    return kafka_consumer
