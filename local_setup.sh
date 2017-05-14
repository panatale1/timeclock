#!/bin/bash

# NEVER run as root
if [[ $(id -u) -eq 0 ]]; then
	echo "Do NOT run as root"
	exit 1
fi


# Expected to be run as the user that will serve the application
VENV_NAME="timeclock"
VENV_DIR="$HOME/.virtualenvs"

# make virtual env base dir if it doesn't exist
mkdir -p $VENV_DIR

# set the workon_home env var if it's not in your .bashrc already
if [[ $(grep WORKON_HOME ~/.bashrc) -ne 0 ]]; then
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
fi

# find the path to virtualenvwrapper.sh script
wrapper_path=$(which virtualenvwrapper.sh)

# source it in bashrc if not already
if [[ wrapper_path != "" ]]; then
	echo $wrapper_path
	if [[ $(grep "source $wrapper_path" ~/.bashrc) == "" ]]; then
		echo "source $wrapper_path" >> ~/.bashrc
		source "$wrapper_path"
	fi
fi

# source it now 
source /usr/local/bin/virtualenvwrapper.sh

# make the venv for this project if it doesn't exist
if [[ ! -e $VENV_DIR/$VENV_NAME ]]; then
	mkvirtualenv $VENV_NAME
fi

# activate the env, install requirements
if [[ -z $(echo $VIRTUAL_ENV) ]]; then
	workon $VENV_NAME
    pip install --upgrade -r requirements.txt
fi

echo "Either run \"source \$(which virtualenvrapper.sh)\" or exit and enter a new shell to enable virtualenvwrapper.sh"

#TODO move to deploy script
#cd $VENV_NAME
#./manage.py syncdb
#./manage.py migrate
