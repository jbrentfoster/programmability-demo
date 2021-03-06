"""Python example script showing proper use of the Cisco Sample Code header.
Copyright (c) {{current_year}} Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

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

__author__ = "Brent Foster <brfoster@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


# KAFKA_TOPIC = 'telegraf'
# KAFKA_BOOTSTRAP_SERVER = '10.135.7.226:9092'
TIMEOUT = 60
TELEMETRY_PATH = ""

def process_telemetry_msg(msg, handler):
    telemetry_encoding_path = "Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface"
    node = "asr9k-01"
    intf_1 = "TenGigE0/0/0/1"
    intf_0 = "TenGigE0/0/0/0"
    # msg = json.loads(kafka_msg.value.decode('utf-8'))
    try:
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
    except Exception as err:
        pass
        # logging.info("Invalid message from kafka.")


class Consumer(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    # daemon = True

    def __init__(self, kafka_consumer, handler):
        self._consumer = kafka_consumer
        super(Consumer, self).__init__()
        self._stop_event = threading.Event()
        self.handler = handler

    def run(self):
        for message in self._consumer:
            # message = str(message)
            # message_decode = message.value.decode("utf-8")
            message_dict = json.loads(message.value.decode("utf-8", errors='ignore'))
            logging.debug("Message received from kafka...")
            # logging.info(json.dumps(message_dict, indent=2, sort_keys=True))
            # logging.info("Telemetry message received.")
            process_telemetry_msg(message_dict, self.handler)
            # self.handler.send_message_open_ws(json.dumps(message_dict, indent=2, sort_keys=True))

    def subscribe(self, topic):
        self._consumer.subscribe(KAFKA_TOPIC)

    def unsubscribe(self):
        self._consumer.unsubscribe()

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


def init_telemetry(handler, kafka_topic, kafka_server, telemetry_path):
    TELEMETRY_PATH = telemetry_path
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    kafka_consumer = KafkaConsumer(kafka_topic, bootstrap_servers=kafka_server)
    my_consumer = Consumer(kafka_consumer, handler)
    # Start the kafka consumer thread.
    my_consumer.start()
    return my_consumer
