#!/usr/bin/env python

import os
import zipfile
import uuid
import shutil
import json
import requests
from docker import Client
from riak import RiakClient
from bottle import *
import git_client

rootdir = os.path.dirname(os.path.abspath(__file__))

if 'DOCKER_HOST' in os.environ:
    docker = Client(base_url=os.environ['DOCKER_HOST'])
else:
    docker = Client()

if not 'RIAK_ADDR' in os.environ:
    raise Exception('$RIAK_ADDR is not defined')

if not 'RIAK_PORT' in os.environ:
    raise Exception('$RIAK_PORT is not defined')

riak = RiakClient(host=os.environ['RIAK_ADDR'], http_port=os.environ['RIAK_PORT'])

def create_instance(version, tag):
    if not tag:
        response = requests.get('http://api.icndb.com/jokes/random?limitTo=nerdy')
        if response.status_code == 200:
            data = json.loads(response.text)
            tag = data['value']['joke']
        else:
            tag = 'none'

    apps = riak.bucket('apps')
    application = apps.new(data='')
    application.store()

    application_id = application.key

    port_bindings = {
        '5432/tcp' : [{ 'HostIp': '', 'HostPort': '' }],
    }
    postgres = start_image('werner/keystone-postgres', ports=['5432'], port_bindings=port_bindings)
    environment = {
        'DB_HOST':postgres['ip'],
        'REVISION': version
    }
    port_bindings = {
        '5000/tcp' : [{ 'HostIp': '', 'HostPort': '' }],
        '35357/tcp' : [{ 'HostIp': '', 'HostPort': '' }]
    }
    keystone = start_image('werner/keystone', environment, ports=['5000', '35357'], port_bindings=port_bindings)

    data = {
        'postgres':postgres,
        'keystone':keystone,
        'version': version,
        'tag': tag
    }

    application.data = json.dumps(data)
    application.store()

    data['id'] = application_id

    return data

def delete_instance(application_id):
    apps = riak.bucket('apps')

    application = apps.get(application_id)
    data = json.loads(application.data)

    for host in [data['postgres'], data['keystone']]:
        docker.kill(host['hostname'])
        docker.remove_container(host['hostname'])

    application.delete()

def start_image(image_name, environment=None, links=None, ports=None, port_bindings=None):
    image = docker.inspect_image(image_name)
    command = image['config']['Cmd']
    volumes = image['config']['Volumes']
    response = docker.create_container(image_name, command, volumes=volumes, environment=environment)
    docker.start(response, port_bindings=port_bindings, links=links)

    info = docker.inspect_container(response)

    mapped_ports = {}

    if port_bindings:
        for port_protocol in port_bindings:
            mapped_port = info['NetworkSettings']['Ports'][port_protocol][0]['HostPort']
            port, protocol = port_protocol.split('/')
            mapped_ports[port] = mapped_port

    return {
        'name': info['Name'][1:],
        'hostname':info['Config']['Hostname'],
        'ip':info['NetworkSettings']['IPAddress'],
        'ports': mapped_ports
    }


@get('/jonah/versions')
def get_versions():
    return json.dumps(git_client.get_versions(rootdir))

@post('/jonah/apps')
def create_application():
    body = request.body.readline()
    info = json.loads(body)
    version = info['version']
    tag = info['tag']
    if not version in git_client.get_versions(rootdir):
        abort(400, 'Version {version} does not exist'.format(version=version))
    return json.dumps(create_instance(version, tag))

@get('/jonah/apps')
def get_applications():
    apps = riak.bucket('apps')
    return json.dumps(apps.get_keys())

@get('/jonah/apps/<application_id>')
def get_application(application_id):
    apps = riak.bucket('apps')
    if not application_id in apps.get_keys():
        abort(404, 'Application {application_id} does not exist'.format(application_id=application_id))
    application = apps.get(application_id)
    data = json.loads(application.data)
    data['id'] = application_id

    return json.dumps(data)

@get('/jonah/hosts/<host_id>/log')
def get_host_log(host_id):
    response.headers['Content-Type'] = 'text/plain; charset=ISO-8859-15'
    try:
        return docker.logs(host_id)
    except:
        abort(404, 'Host {host_id} does not exist'.format(host_id=host_id))

@delete('/jonah/apps/<application_id>')
def delete_application(application_id):
    apps = riak.bucket('apps')
    if not application_id in apps.get_keys():
        abort(404, 'Application {application_id} does not exist'.format(application_id=application_id))
    delete_instance(application_id)

@get('/')
def get_index():
    return static_file('index.html', root=rootdir)

@get('/static/<path:path>')
def get_index(path):
    return static_file(path, root=os.path.join(rootdir, 'static'))


if __name__ == "__main__":
    run(host='0.0.0.0', port=8081, reloader=True, server='paste')
else:
    application = default_app()
