jonah
==================

#QuickStart

#Docker
In order to use jonah you will need to install Docker.

Setup Docker host for remote management, start Docker with the following options:

`-d -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock`

This will enable both the socket support and TCP.

If you are installing on Ubuntu you can edit `/etc/init/docker.conf` and at the above options $DOCKER_OPTS:

    DOCKER_OPTS="-d -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock"

Or more conveniently on ubuntu:

```
sudo sed -i \
's,DOCKER_OPTS=.*,DOCKER_OPTS=\"-d -H tcp://0.0.0.0:4243 -H unix:///var/run/docker.sock\",' \
/etc/init/docker.conf
```

##Security Note
Currently there is no authentication in Docker itself. Since jonah needs to remotely manage the host, you must make sure to place it on a private network otherwise any host will be able to connect to it.

#jonah

Once you have Docker installed and running, pull the keystone and jonah images:

```
docker pull werner/riak
docker pull werner/keystone
docker pull werner/keystone-postgres
docker pull werner/jonah
```

To run the latest version on port 8080:

```
pip install fig
fig up
```

#Client
There is a provided client that can be used to manage the remote service.

Available commands are specified by running the client:

`./client.py`

Additional help can be retrieved from the available commands:

`./client.py versions -h`
