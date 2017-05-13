#1/bin/bash

# Only run as root
if [[ $(id -u) -ne 0 ]]; then
	echo "Please run as root"
	exit 1
fi

# set package list empty
packages=""

# add python reqs to package list
if [ $(which python) == "" ]; then
    packages+=" python python-dev"
else
	echo "Python already installed"
fi

# Add pip reqs to package list
pip=$(which pip)
if [[ "$?" -ne 0 ]]; then
    packages+=" python-pip"
fi

# add other reqs to package list
packages+=" libpq-dev postgresql postgresql-contrib nginx python-software-properties nodejs npm"

add-apt-repository ppa:chris-lea/node.js -y
apt-get update

# install packages
apt-get install $packages -y

# create the db user (running as root simplify the su-ing
su -c 'psql -a -f django.psql' postgres

# Install npm global requirements
npm install -g less@1.7.5

# Install pip global packages
pip install --upgrade pip setuptools wheel virtualenv virtualenvwrapper
