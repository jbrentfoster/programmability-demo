Sample web server and client application.  Can be used for prototyping and demonstrations.  Uses tornado web server framework and javascript client.

Key Cisco technologies:
- YANG Development Kit (YDK)
- Streaming telemetry (via Kafka)

Pre-requisites:

You must have a working Python3 virtual environment with Cisco YANG Development kit (YDK) packages installed.  For YDK installation please refer to

https://github.com/CiscoDevNet/ydk-py

Please make sure to review and install the minimum libraries described in the System Requirements for YDK.

Example steps:

`virtualenv -p python3 ydk-python3-venv`

`source ydk-python3-venv/bin/activate`

`pip install ydk`

`pip install ydk-models-cisco-ios-xr`

`pip install ydk-models-openconfig`

When completed your virtual environment should have the following packages installed:

```(test-ydk-venv)$ pip list

Package                 Version
pip                     19.3.1
pybind11                2.4.3
setuptools              44.0.0
wheel                   0.33.6
ydk                     0.8.4
ydk-models-cisco-ios-xr 6.6.2
ydk-models-openconfig   0.1.6.post1```

Remaining setup instructions:

1) Activate virtual environment as per pre-requisites section above.  Example,

source ydk-python3-venv/bin/activate

2) Install required packages.

pip install requests
pip install tornado
pip install kafka

3) Clone the repo to your local machine:

$ git clone https://github.com/jbrentfoster/programmability-demo.git

To start the server:

cd programmability-demo
python server.py --port [port number]

Example,

    (python3.7-venv) python server.py --port 8000
    
Open a Web browser and enter the URL, example

http://127.0.0.1:8000/

Note that the example will only work with Cisco IOS-XR devices running 6.x or later.

For telemetry page to work properly, you must have a working telemetry collection stack with a Kafka topic.

In the telemetry_code.py file edit the following lines:
KAFKA_TOPIC = 'telegraf'
KAFKA_BOOTSTRAP_SERVER = 'localhost:9092'

Other custimization of the code within that file will be required such as the node name, telemetry xpath, etc.