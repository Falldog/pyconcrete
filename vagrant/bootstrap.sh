#!/usr/bin/env bash

sudo apt-get update
sudo apt-get install -y vim
sudo apt-get install -y python-pip

sudo apt-get install -y python-software-properties
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

sudo apt-get install -y python3.3 python3.3-dev
sudo apt-get install -y python3.4 python3.4-dev
sudo apt-get install -y python3.5 python3.5-dev
sudo apt-get install -y python3.6 python3.6-dev
sudo apt-get install -y python3.7 python3.7-dev

sudo apt-get install -y pandoc
sudo pip install pypandoc
sudo pip install twine
