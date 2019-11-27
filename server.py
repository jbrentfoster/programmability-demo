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

# global variables...
initial_url = "https://jsonplaceholder.typicode.com/posts"
# node_ip = "192.168.0.1"
# node_user = "cisco"
# node_pass = "cisco"
open_websockets = []
telemetry_thread = None
telemetry_url = "http://192.168.5.102:3000/d/E5LFSC1Wz/telegraf?from=1574451327540&to=1574472927540&orgId=1&theme=light"

class IndexHandler(tornado.web.RequestHandler):

    async def get(self):
        global telemetry_thread
        await self.render("templates/index.html", port=args.port)
        if telemetry_thread is not None:
            telemetry_thread.pause()


class AjaxHandler(tornado.web.RequestHandler):

    async def post(self):
        global initial_url
        global node_ip
        global node_user
        global node_pass

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

        if action == 'send-request':
            initial_url = request['url']
            methods.send_request(self, request)
            # methods.execute_ydk(self, request)
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
        global telemetry_thread
        global telemetry_url
        self.render("templates/telemetry_template.html", port=args.port, telemetry_url=telemetry_url)
        if telemetry_thread is None:
            telemetry_thread = telemetry_code.init_telemetry(self)
        else:
            telemetry_thread.resume()

    def send_message_open_ws(self, message):
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
