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

import json
import logging
# from server import clean_files as clean_files
from server_code import utils
from server_code import ydk_code

__author__ = "Brent Foster <brfoster@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


def send_request(ajax_handler, request):
    # clean_files()
    response_json_list = []
    try:
        ajax_handler.send_message_open_ws("Sending REST call..")
        response = utils.rest_get_json(request['url'], "", "foo", "bar")
        response_json = json.loads(response)
        if type(response_json) is dict:
            response_json_list.append(response_json)
            response = json.dumps(response_json_list, indent=2, sort_keys=True)
        ajax_handler.send_message_open_ws(response)
        logging.info(response)
        with open("jsongets/response.json", 'w', encoding="utf8") as f:
            # json.dump(response, f, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(response)
            f.close()
        result = {'action': 'collect', 'status': 'completed'}
        logging.info(result)
        ajax_handler.write(json.dumps(result))
    except Exception as err:
        result = {'action': 'collect', 'status': 'failed'}
        logging.info(result)
        ajax_handler.write(json.dumps(result))

def execute_ydk(ajax_handler, request):
    try:
        provider = None
        for tmp_provider in ydk_code.nc_providers:
            if tmp_provider['node-ip'] == request['node-ip']:
                provider = tmp_provider['provider']
        if provider is None:
            provider_dict = ydk_code.create_netconf_provider(request)
            provider = provider_dict['provider']
            ydk_code.nc_providers.append(provider_dict)
        ydk_code.create_l3_service(request, provider)
        result = {'action': request['action'], 'status': 'completed'}
        logging.info(result)
        ajax_handler.write(json.dumps(result))
    except Exception as err:
        result = {'action': request['action'], 'status': 'failed'}
        logging.info(result)
        logging.info(err)
        ajax_handler.write(json.dumps(result))

def get_response():
    with open("jsongets/response.json", 'r', ) as f:
        response = json.load(f)
        f.close()
    return json.dumps(response)