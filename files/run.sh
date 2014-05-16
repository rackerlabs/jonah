#!/usr/bin/env bash

if [ -z "$DOCKER_HOST" ]; then
    export DOCKER_HOST='http://172.17.42.1:4243'
fi


if [ -n "$RIAK_PORT_8098_TCP_ADDR" ]; then
    export RIAK_ADDR=$RIAK_PORT_8098_TCP_ADDR
fi

if [ -n "$RIAK_PORT_8098_TCP_PORT" ]; then
    export RIAK_PORT=$RIAK_PORT_8098_TCP_PORT
fi


if [ -n "$RIAK_1_PORT_8098_TCP_ADDR" ]; then
    export RIAK_ADDR=$RIAK_1_PORT_8098_TCP_ADDR
fi

if [ -n "$RIAK_1_PORT_8098_TCP_PORT" ]; then
    export RIAK_PORT=$RIAK_1_PORT_8098_TCP_PORT
fi

sed -i -e s,_RIAK_ADDR,$RIAK_ADDR,g -e s,_RIAK_PORT,$RIAK_PORT,g -e s,_DOCKER_HOST,$DOCKER_HOST,g /etc/uwsgi/apps-enabled/uwsgi.ini

(cd keystone && git pull)

service nginx start
ln -s /proc/self/fd /dev/fd
service uwsgi start

chown www-data:www-data /var/www/jonah/files
tail -f /var/log/nginx/access.log -f /var/log/nginx/error.log
