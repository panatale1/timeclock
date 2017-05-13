#!/bin/bash

# MUST BE RUN AS ROOT FROM SAME DIRECTORY AS DJANGO.PSQL
VENV_NAME="timeclock"
VENV_DIR="$HOME/.virtualenvs"

mkdir -p $VENV_DIR

if [[ $(grep WORKON_HOME ~/.bashrc) == "" ]]; then
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
fi

wrapper_path=$(which virtualenvwrapper.sh)
if [[ wrapper_path != "" ]]; then
	echo $wrapper_path
	if [[ $(grep "source $wrapper_path" ~/.bashrc) == "" ]]; then
		echo "source $wrapper_path" >> ~/.bashrc
		source "$wrapper_path"
	fi
fi
source /usr/local/bin/virtualenvwrapper.sh
if [[ ! -e $VENV_DIR/$VENV_NAME ]]; then
	mkvirtualenv $VENV_NAME
fi
if [[ -z $(echo $VIRTUAL_ENV) ]]; then
	workon $VENV_NAME
fi
apt-get install python-software-properties
add-apt-repository ppa:chris-lea/node.js
apt-get update
apt-get install nodejs npm
npm install -g less@1.7.5
pip install --upgrade -r requirements.txt
apt-get install postgresql
<<<<<<< HEAD
su -c 'psql -a -f django.psql' postgres
#cd $VENV_NAME
#./manage.py syncdb
#./manage.py migrate
=======
su postgres
psql -a -f django.psql
echo "exit"
cd $VENV_NAME
./manage.py syncdb
./manage.py migrate
>>>>>>> 71270ff891a658807fe93e0cfec4df3bd8a6c2c0
