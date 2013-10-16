# jonah
#
# VERSION               0.1

FROM ubuntu:14.04
MAINTAINER Werner R. Mendizabal "werner.mendizabal@gmail.com"

RUN apt-get install -y curl git-core nginx openssh-server python-pip uwsgi uwsgi-plugin-python

RUN pip install virtualenv

ADD . /var/www/jonah

RUN virtualenv /var/www/jonah/env

RUN . /var/www/jonah/env/bin/activate && pip install -r /var/www/jonah/tools/requirements

WORKDIR /var/www/jonah

ADD files/run.sh /var/www/jonah/run.sh
ADD files/default /etc/nginx/sites-enabled/default
ADD files/uwsgi.ini /etc/uwsgi/apps-enabled/uwsgi.ini

RUN mkdir -p /var/www/jonah/files

RUN chown -R www-data:www-data /var/www/jonah

RUN sed -i s/www-data/root/ /etc/nginx/nginx.conf

RUN git clone https://github.com/openstack/keystone.git

EXPOSE 22 80

CMD ./run.sh
