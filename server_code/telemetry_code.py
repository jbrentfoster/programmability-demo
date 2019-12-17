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

KAFKA_TOPIC = 'telegraf'
KAFKA_BOOTSTRAP_SERVER = 'localhost:9092'
TIMEOUT = 60


# def validate_bgp_peer(kafka_consumer, node, peer_address,
#                       session_state=SESSION_STATE_ESTABLISHED,
#                       timeout=TIMEOUT):
#     """Validate BGP session state."""
#     telemetry_encoding_path = "openconfig-network-instance:network-instances/network-instance/protocols/protocol/bgp/neighbors/neighbor"
#     start_time = time.time()
#     for kafka_msg in kafka_consumer:
#         msg = json.loads(kafka_msg.value.decode('utf-8'))
#         if (msg["Telemetry"]["node_id_str"] == node and
#                 msg["Telemetry"]["encoding_path"] == telemetry_encoding_path
#                 and "Rows" in msg):
#             for row in msg["Rows"]:
#                 if ("neighbor-address" in row["Keys"] and
#                         row["Keys"]["neighbor-address"] == peer_address and
#                         "state" in row["Content"] and
#                         "session-state" in row["Content"]["state"] and
#                         row["Content"]["state"]["session-state"] == session_state):
#                     return True
#
#         if time.time() - start_time > timeout:
#             break
#
#     return False

def process_telemetry_msg(msg, handler):
    telemetry_encoding_path = "Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface"
    node = "asr9k-01"
    intf_1 = "TenGigE0/0/0/1"
    intf_0 = "TenGigE0/0/0/0"
    # msg = json.loads(kafka_msg.value.decode('utf-8'))
    logging.debug("Kafka message is from " + msg['tags']['Producer'] + "...")
    if (msg["tags"]["Producer"] == node and
            msg["name"] == telemetry_encoding_path
            and "fields" in msg):
        try:
            if_name = msg['tags']['interface-name']
            output_rate = msg['fields']['data-rates/output-data-rate']
            if if_name == intf_1 or if_name == intf_0:
                msg_text = "Kafka message: " + msg["tags"]["Producer"] + " " + if_name + " output rate: " + str(output_rate) + " kbps"
                handler.send_message_open_ws(msg_text)
        except Exception as err:
            pass


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
            # message_decode = message.value.decode("utf-8")
            message_dict = json.loads(message.value.decode("utf-8", errors='ignore'))
            logging.debug("Message received from kafka...")
            # logging.info(json.dumps(message_dict, indent=2, sort_keys=True))
            process_telemetry_msg(message_dict, self.handler)
            # self.handler.send_message_open_ws(json.dumps(message_dict, indent=2, sort_keys=True))

    def subscribe(self, topic):
        self._consumer.subscribe(KAFKA_TOPIC)

    def close(self):
        self._consumer.close()

    def pause(self):
        logging.info("Pausing kafka consumer subscription...")
        partitions = list(self._consumer.assignment())
        partition = partitions[0]
        # partition = TopicPartition(topic=KAFKA_TOPIC, partition=0)
        self._consumer.pause(partition)

    def resume(self):
        logging.info("Resuming kafka consumer subscription...")
        partitions = list(self._consumer.assignment())
        partition = partitions[0]
        # partition = TopicPartition(topic=KAFKA_TOPIC, partition=0)
        self._consumer.resume(partition)

    def stop(self):
        logging.info("Halting telemetry thread...")
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


def init_telemetry(handler):
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    kafka_consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVER)
    my_consumer = Consumer(kafka_consumer, handler)
    # Start the kafka consumer thread.
    my_consumer.start()
    return my_consumer
