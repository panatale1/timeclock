#!/bin/bash
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
pip install --upgrade -r requirements.txt
cd $VENV_NAME
./manage.py syncdb
./manage.py migrate
