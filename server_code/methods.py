import json
import logging
# from server import clean_files as clean_files
from server_code import utils
from server_code import ydk_code


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
        # output = ydk_code.process_isis("192.168.0.7", 830, "cisco", "cisco", "ssh")
        # logging.info(output)
        # ajax_handler.send_message_open_ws(output)
        ydk_code.create_uni(request['node-ip'], 830, request['node-user'], request['node-pass'], "ssh",
                            request['interface-name'], int(request['load-interval']))
        result = {'action': 'collect', 'status': 'completed'}
        logging.info(result)
        ajax_handler.write(json.dumps(result))
    except Exception as err:
        result = {'action': 'collect', 'status': 'failed'}
        logging.info(result)
        ajax_handler.write(json.dumps(result))

def get_response():
    with open("jsongets/response.json", 'r', ) as f:
        response = json.load(f)
        f.close()
    return json.dumps(response)