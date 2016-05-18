#!/usr/bin/env python
import json
import requests
import sys
import os


def _get_file_contents(filename):
    with open(filename, 'r') as fd:
        return fd.read()


def _construct_headers():
    headers = {
        'Content-Type': 'application/xml',
        'Accept': 'application/json'
    }
    return headers


def post(endpoint_url, filename):
    data = _get_file_contents(filename)
    headers = _construct_headers()
    response = requests.post(endpoint_url, data=data, headers=headers)
    print "HTTP status: %d %s" % (response.status_code, response.reason)
    print json.dumps(response.json(), indent=4)


def main(*args):
    dir_name = args[0][0]
    for file_ in os.listdir(dir_name):
        file_path = os.path.join(dir_name, file_)
        post("http://edge.localdomain:9000/adapter/certuk_mod/import/admin", file_path)


# directory_inboxing.py full_path_to_directory_to_iterate_over
if __name__ == '__main__':
    main(sys.argv[1:])
