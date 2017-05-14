#!/bin/bash

# Only run as root
if [[ $(id -u) -ne 0 ]]; then
	echo "Please run as root"
	exit 1
fi

# set package list empty
packages=""

# add python reqs to package list
if [ $(which python) == "" ]; then
    packages+=" python"
else
	echo "Python already installed"
fi

# Add pip reqs to package list
pip=$(which pip)
if [[ "$?" -ne 0 ]]; then
    packages+=" python-pip"
fi

# add other reqs to package list
packages+=" python-dev libpq-dev postgresql postgresql-contrib nginx python-software-properties nodejs"

echo "installing these packages: $packages"

add-apt-repository ppa:chris-lea/node.js -y
apt-get update

# install packages
apt-get install $packages -f -y

# for some reason this one needs to run after the previous
apt-get install npm -y

# create the db user (running as root simplify the su-ing
su -c 'psql -a -f django.psql' postgres

# Install npm global requirements
npm install -g less@1.7.5

# Install pip global packages
pip install --upgrade pip setuptools wheel

# uses the new pip
pip install --upgrade virtualenv virtualenvwrapper

echo "Sign out of root account and run local_setup.sh as app user"
