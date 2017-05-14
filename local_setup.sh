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
else
    echo "workon_home already set to $VENV_DIR"
fi

# find the path to virtualenvwrapper.sh script
wrapper_path=$(which virtualenvwrapper.sh)

# source it in bashrc if not already
if [[ wrapper_path != "" ]]; then
	echo "found virtualenvwrapper.sh at $wrapper_path"
	if [[ $(grep "source $wrapper_path" ~/.bashrc) == "" ]]; then
		echo "source $wrapper_path" >> ~/.bashrc
        echo "added sourcing of $wrapper_path to .bashrc"
    else
        echo "$wrapper_path already being sourced in .bashrc, no need to add it"
	fi
else
    echo "virtualenvwrapper.sh not found in path! Your VENV Won't be created!"
    echo "try opening a new shell and running this again to ensure virtualenvwrapper.sh is loaded"
fi

# make the venv for this project if it doesn't exist
if [[ ! -e $VENV_DIR/$VENV_NAME ]]; then
    # use virtualenv normally, trying to use virtualenvwrapper.sh in a bash
    # script is an exercise in masochism
    virtualenv $VENV_DIR/$VENV_NAME
    echo "created new virtualenv at $VENV_NAME"
else
    echo "the venv dir $VENV_NAME was found. This is probably not the first time this script has been run! (No big deal, really)"
fi

# activate the env, install requirements
if [[ -z $(echo $VIRTUAL_ENV) ]]; then
    # same for activating a venv in bash script, so it w/o the wrapper
	source $VENV_DIR/$VENV_NAME/bin/activate
    # now the req's get installed inside the venv
    pip install --upgrade -r requirements.txt
fi

echo "Either run \"source \$(which virtualenvrapper.sh)\" or exit and enter a new shell to enable virtualenvwrapper.sh"

#TODO move to deploy script
#cd $VENV_NAME
#./manage.py syncdb
#./manage.py migrate
