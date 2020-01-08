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

"""
Creates an HTTP server with basic websocket communication.
"""
import argparse
from datetime import datetime
from time import sleep
import json
import os
import traceback
import tornado.web
import tornado.websocket
import tornado.escape
import tornado.ioloop
import tornado.locks
from kafka import KafkaConsumer
import threading
from tornado.web import url
from server_code import methods
from server_code import telemetry_code
import logging
from distutils.dir_util import remove_tree
from distutils.dir_util import mkpath

__author__ = "Brent Foster <brfoster@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

# global variables...
open_websockets = []
telemetry_thread = None
telemetry_encoding_path = "Cisco-IOS-XR-pfi-im-cmd-oper:interfaces/interface-xr/interface"
telemetry_url = "http://192.168.5.102:3000/d/If-Nz2-Zk/verizon-segment-routing-demo-asr9k-01?orgId=1&refresh=10s&from=1575919364336&to=1575921164336&theme=light"
KAFKA_TOPIC = 'telegraf'
KAFKA_BOOTSTRAP_SERVER = '10.135.7.226:9092'


class IndexHandler(tornado.web.RequestHandler):

    async def get(self):
        global telemetry_thread
        await self.render("templates/index.html", port=args.port)
        if telemetry_thread is not None:
            telemetry_thread.pause()


class AjaxHandler(tornado.web.RequestHandler):

    async def post(self):
        global node_ip
        global node_user
        global node_pass
        global KAFKA_BOOTSTRAP_SERVER
        global KAFKA_TOPIC
        global telemetry_encoding_path
        global telemetry_thread

        request_body = self.request.body.decode("utf-8")
        # request = tornado.escape.recursive_unicode(self.request.arguments)
        logging.info("Received AJAX request..")
        logging.info(request_body)
        request = json.loads(request_body)

        try:
            action = request['action']
        except Exception as err:
            logging.warning("Invalid AJAX request")
            logging.warning(err)
            response = {'status': 'failed', 'error': err}
            logging.info(response)
            self.write(json.dumps(response))

        if action == 'update-telemetry':
            logging.info("Telemetry update...")
            KAFKA_BOOTSTRAP_SERVER = request['kafka-ip']
            KAFKA_TOPIC = request['kafka-topic']
            telemetry_encoding_path = request['telemetry-path']
            if telemetry_thread is None:
                try:
                    telemetry_thread = telemetry_code.init_telemetry(self, kafka_server=KAFKA_BOOTSTRAP_SERVER,
                                                                     kafka_topic=KAFKA_TOPIC,
                                                                     telemetry_path=telemetry_encoding_path)
                except Exception as err:
                    logging.error("Connection to kafka server could not be established!")
            else:
                telemetry_thread.resume()
        elif action == 'execute-config':
            node_ip = request['node-ip']
            node_user = request['node-user']
            node_pass = request['node-pass']
            methods.execute_ydk(self, request)
        else:
            logging.warning("Received request for unknown operation!")
            response = {'status': 'unknown', 'error': "unknown request"}
            logging.info(response)
            self.write(json.dumps(response))

    def send_message_open_ws(self, message):
        for ws in open_websockets:
            ws.send_message(message)


class TelemetryHandler(tornado.web.RequestHandler):

    def get(self):
        if telemetry_thread is not None:
            telemetry_thread.resume()
            gray_button = True
        global telemetry_thread
        # TODO Gray out button if telemetry threading has already started
        global telemetry_url
        self.render("templates/telemetry_template.html", port=args.port, telemetry_url=telemetry_url,
                    kafka_ip=KAFKA_BOOTSTRAP_SERVER, kafka_topic=KAFKA_TOPIC, telemetry_path=telemetry_encoding_path)


    def send_message_open_ws(self, message):
        if len(open_websockets) == 0:
            logging.info("Currently no open websockets, discarding message.")
        for ws in open_websockets:
            ws.send_message(message)


class ResponseHandler(tornado.web.RequestHandler):

    def get(self):
        response = methods.get_response()
        self.render("templates/response_template.html", response=response)


class ReferencesHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("templates/references_template.html")


class WebSocket(tornado.websocket.WebSocketHandler):

    def open(self):
        logging.info("WebSocket opened")
        open_websockets.append(self)

    def send_message(self, message):
        self.write_message(message)

    def on_message(self, message):
        """Evaluates the function pointed to by json-rpc."""
        json_rpc = json.loads(message)
        logging.info("Websocket received message: " + json.dumps(json_rpc))

        try:
            result = getattr(methods,
                             json_rpc["method"])(**json_rpc["params"])
            error = None
        except:
            # Errors are handled by enabling the `error` flag and returning a
            # stack trace. The client can do with it what it will.
            result = traceback.format_exc()
            error = 1

        json_rpc_response = json.dumps({"result": result, "error": error,
                                        "id": json_rpc["id"]},
                                       separators=(",", ":"))
        logging.info("Websocket replied with message: " + json_rpc_response)
        self.write_message(json_rpc_response)

    def on_close(self):
        logging.info("Websocket closing...")
        open_websockets.remove(self)
        logging.info("WebSocket closed!")


def main():
    # Set up logging
    try:
        os.remove('collection.log')
    except Exception as err:
        logging.info("No log file to delete...")

    logFormatter = logging.Formatter('%(levelname)s:  %(message)s')
    rootLogger = logging.getLogger()
    rootLogger.level = logging.INFO

    fileHandler = logging.FileHandler(filename='collection.log')
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info("Starting webserver...")
    current_time = str(datetime.now().strftime('%Y-%m-%d-%H%M-%S'))
    logging.info("Current time is: " + current_time)
    settings = {
        # "static_path": os.path.join(os.path.dirname(__file__), "static"),
        "static_path": os.path.normpath(os.path.dirname(__file__)),
        # "cookie_secret": "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        # "login_url": "/login",
        # "xsrf_cookies": True,
    }

    handlers = [url(r"/", IndexHandler, name="home"),
                url(r"/websocket", WebSocket),
                url(r'/static/(.*)',
                    tornado.web.StaticFileHandler,
                    dict(path=settings['static_path'])),
                url(r'/telemetry', TelemetryHandler, name="telemetry"),
                url(r'/response', ResponseHandler, name="response"),
                url(r'/references', ReferencesHandler, name="references"),
                url(r'/ajax', AjaxHandler, name="ajax")
                ]

    application = tornado.web.Application(handlers)
    application.listen(args.port)

    # webbrowser.open("http://localhost:%d/" % args.port, new=2)

    loop = tornado.ioloop.IOLoop.instance()
    try:
        loop.start()
    except KeyboardInterrupt:
        loop.stop()
    # tornado.ioloop.IOLoop.instance().start()
    # tornado.ioloop.IOLoop.current().start()


def clean_files():
    # Delete all output files
    logging.info("Cleaning files from last collection...")
    try:
        remove_tree('jsonfiles')
        remove_tree('jsongets')
    except Exception as err:
        logging.info("No files to cleanup...")

    # Recreate output directories
    mkpath('jsonfiles')
    mkpath('jsongets')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Starts a webserver for stuff.")
    parser.add_argument("--port", type=int, default=8000, help="The port on which "
                                                               "to serve the website.")
    args = parser.parse_args()
    main()
