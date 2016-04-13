#!/usr/bin/env python
import json
import requests

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


def main():
    post("http://0.0.0.0:9000/adapter/certuk_mod/import/admin", '/home/andy/Downloads/obs_purplesecure_observable-108fb72e-ec78-4cea-956d-64cd54bb7f75.xml')


if __name__ == '__main__':
    main()
