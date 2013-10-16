#!/usr/bin/env python

import argparse
import json
import requests
import sys

host = 'http://localhost:8080'

headers = {'content-type':'application/json', 'accept':'application/json'}

def format_json(text):
    return json.dumps(json.loads(text), sort_keys=True, indent=4)

def list_versions():
    result = requests.get('{host}/jonah/versions'.format(host=host), verify=False)
    if result.status_code == 200:
        return format_json(result.text)

def list_apps():
    result = requests.get('{host}/jonah/apps'.format(host=host), verify=False)
    if result.status_code == 200:
        return format_json(result.text)

def get_app(app_id):
    result = requests.get('{host}/jonah/apps/{app_id}'.format(host=host,app_id=app_id), verify=False)
    if result.status_code == 200:
        return format_json(result.text)

def get_app_log(host_id):
    result = requests.get('{host}/jonah/hosts/{host_id}/log'.format(host=host,host_id=host_id), verify=False)
    if result.status_code == 200:
        return result.text

def create_app(version, tag):
    request = {
        'version': version,
        'tag': tag
    }
    body = json.dumps(request)
    result = requests.post('{host}/jonah/apps'.format(host=host), body, verify=False)
    if result.status_code == 200:
        return format_json(result.text)

def delete_app(app_id):
    result = requests.delete('{host}/jonah/apps/{app_id}'.format(host=host,app_id=app_id), verify=False)

parser = argparse.ArgumentParser(description='Cloud Identity as a Service Client')
subparsers = parser.add_subparsers(help='available options')

version_parser = subparsers.add_parser('versions')
version_parser.set_defaults(func=list_versions)

create_parser = subparsers.add_parser('create')
create_parser.add_argument('version')
create_parser.add_argument('tag')
create_parser.set_defaults(func=create_app)

get_parser = subparsers.add_parser('get')
get_parser.add_argument('app_id')
get_parser.set_defaults(func=get_app)

log_parser = subparsers.add_parser('log')
log_parser.add_argument('host_id')
log_parser.set_defaults(func=get_app_log)

list_parser = subparsers.add_parser('list')
list_parser.set_defaults(func=list_apps)

delete_parser = subparsers.add_parser('delete')
delete_parser.add_argument('app_id')
delete_parser.set_defaults(func=delete_app)


if len(sys.argv) > 1:
    args = vars(parser.parse_args())
else:
    sys.argv.append('-h')
    parser.parse_args()

func = args['func']
del args['func']

print func(**args)
