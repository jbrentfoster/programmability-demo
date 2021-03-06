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

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import json
from server_code import errors
import xml.dom.minidom
import logging

__author__ = "Brent Foster <brfoster@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


urllib3.disable_warnings(InsecureRequestWarning)


def rest_get_json(baseURL, uri, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/json'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.get(restURI, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        # print "HTTP response code is: " + str(r.status_code)
        if r.status_code == 200:
            return json.dumps(r.json(), indent=2)
        else:
            raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return


def rest_get_xml(baseURL, uri, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/xml'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.get(restURI, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        # print "HTTP response code is: " + str(r.status_code)
        if r.status_code == 200:
            response_xml = xml.dom.minidom.parseString(r.content)
            return response_xml.toprettyxml()
        else:
            raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return


def rest_post_xml(baseURL, uri, thexml, user, password):
    proxies = {
        "http": None,
        "https": None,
    }
    appformat = 'application/xml'
    headers = {'content-type': appformat, 'accept': appformat}
    restURI = baseURL + uri
    logging.info(restURI)
    try:
        r = requests.post(restURI, data=thexml, headers=headers, proxies=proxies, auth=(user, password), verify=False)
        logging.error("HTTP response code is: " + str(r.status_code))
        if r.status_code == 200:
            response_xml = xml.dom.minidom.parseString(r.content)
            return response_xml.toprettyxml()
        else:
            logging.warning("Failed XML post!")
            logging.warning("HTTP status code: " + str(r.status_code))
            # raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code) + "\n" + r.content)
    except errors.InputError as err:
        logging.error("Exception raised: " + str(type(err)))
        logging.error(err.expression)
        logging.error(err.message)
        return

def rest_post_json(baseURL, uri, thejson, user, password):
        proxies = {
            "http": None,
            "https": None,
        }
        appformat = 'application/json'
        headers = {'content-type': appformat, 'accept': appformat}
        restURI = baseURL + uri
        logging.info(restURI)
        try:
            r = requests.post(restURI, data=thejson, headers=headers, proxies=proxies, auth=(user, password),
                              verify=False)
            # print "HTTP response code is: " + str(r.status_code)
            if r.status_code == 200:
                return json.dumps(r.json(), indent=2)
            else:
                raise errors.InputError(restURI, "HTTP status code: " + str(r.status_code))
        except errors.InputError as err:
            logging.error("Exception raised: " + str(type(err)))
            logging.error(err.expression)
            logging.error(err.message)
            return

# def cleanxml(thexml):
#     cleanedupXML = "".join([s for s in thexml.splitlines(True) if s.strip("\r\n\t")])
#     return cleanedupXML
