Sample web server and client application.  Can be used for prototyping and demonstrations.  Uses tornado web server framework and javascript client.

Key Cisco technologies:
YANG Development Kit (YDK)
Streaming telemetry (via Kafka)

Setup Instructions

1) Create a Python 3.7 virtual environment (or latest Python 3 distribution).

2) Activate the virtual environment.

3) Install required packages.

`pip install -r requirements.txt`



To start the server:

`python server.py --port [port number]`

Example,

    (python3.7-venv) python server.py --port 8000`
    
Open a Web browser and enter the URL, example

`http://127.0.0.1:8000/`

For telemetry page to work properly, you must have a working telemetry collection stack with a Kafka topic.

In the telemetry_code.py file edit the following lines:
KAFKA_TOPIC = 'telegraf'
KAFKA_BOOTSTRAP_SERVER = '10.135.7.226:9092'

Other custimization of the code within that file will be required such as the node name, telemetry xpath, etc.