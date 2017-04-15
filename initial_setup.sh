#!/bin/bash

if [[ $(id -u_ -ne 0 ]]; then
	echo "Please run as root"
	exit 1
fi
if [ $(which python) == "" ]; then
	apt-get install python
else
	echo "Python already installed"
fi
pip = $(which pip)
if [["$?" -ne 0 ]]; then
	apt-get install --upgrade python-pip
fi
pip install virtualenv
pip install virtualenvwrapper

mkdir -p ~/.virtualenvs

if [[ $(grep WORKON_HOME ~/.bashrc) -ne 0 ]]; then
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
fi
