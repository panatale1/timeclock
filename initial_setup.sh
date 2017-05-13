#1/bin/bash

<<<<<<< Updated upstream
if [[ $(id -u) -ne 0 ]]; then
=======
if [[ $(id -u -ne 0) ]]; then
>>>>>>> Stashed changes
	echo "Please run as root"
	exit 1
fi
if [ $(which python) == "" ]; then
	apt-get install python
else
	echo "Python already installed"
fi
pip=$(which pip)
<<<<<<< Updated upstream
if [["$?" -ne 0]]; then
	apt-get install -u python-pip
=======
if [[ "$?" -ne 0 ]]; then
	apt-get install --upgrade python-pip
>>>>>>> Stashed changes
fi
pip install virtualenv
pip install virtualenvwrapper

mkdir -p ~/.virtualenvs
if [[ $(grep WORKON_HOME ~/.bashrc) -ne 0 ]]; then
	echo "export WORKON_HOME=~/.virtualenvs" >> ~/.bashrc
fi
