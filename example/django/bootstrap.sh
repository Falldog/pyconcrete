#!/usr/bin/env bash

USER=ubuntu

PYE_HOME=/home/pye_web          # encrypted
PYE_HOME_SRC=/home/pye_web_src  # source
PYE_LOG_DIR=/var/log/pye_web
PYCONCRETE_HOME=/home/pyconcrete


setup_python()
{
    sudo apt-get install -y python-software-properties
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get update

    sudo apt-get install -y python2.7 python2.7-dev
    #sudo apt-get install -y python3.3 python3.3-dev
    #sudo apt-get install -y python3.4 python3.4-dev
    #sudo apt-get install -y python3.5 python3.5-dev
    #sudo apt-get install -y python3.6 python3.6-dev
}

setup_nginx()
{
    sudo apt-get install -y nginx
    sudo apt-get install -y uwsgi
    sudo apt-get install -y supervisor

    # uwsgi + supervisor
    sudo mkdir -p /etc/uwsgi
    sudo cp /vagrant/config/uwsgi/pye-web-uwsgi.ini /etc/uwsgi

    sudo cp /vagrant/config/supervisor/uwsgi.conf /etc/supervisor/conf.d
    sudo supervisorctl reload

    # nginx
    sudo cp /vagrant/config/uwsgi/uwsgi_param /etc/nginx
    sudo cp /vagrant/config/nginx/nginx.conf /etc/nginx
    sudo cp /vagrant/config/nginx/pye-web-uwsgi.conf /etc/nginx/sites-enabled

    sudo service nginx reload
}

setup_pyconcrete()
{
    cd $PYCONCRETE_HOME
    sudo python setup.py install <<STDIN
pyconcrete
pyconcrete
STDIN

}

setup_pye_web()
{
    sudo mkdir -p $PYE_HOME
    sudo chown $USER:$USER $PYE_HOME
    cp -r $PYE_HOME_SRC/* $PYE_HOME
    pyconcrete-admin.py compile --source=$PYE_HOME --pye --remove-py --remove-pyc  -i wsgi.py manage.py

    sudo supervisorctl restart uwsgi
}

sudo apt-get update
sudo apt-get install -y python-pip

sudo pip install -r $PYE_HOME_SRC/requirements.txt
sudo mkdir -p $PYE_LOG_DIR
sudo chown $USER:$USER $PYE_LOG_DIR

setup_python
setup_nginx
setup_pyconcrete
setup_pye_web

