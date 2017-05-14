#!/bin/bash

NAME="timeclock"
DJANGODIR=/home/repos/timeclock/timeclock
SOCKFILE=/home/repos/timeclock/run/gunicorn.sock
NUM_WORKERS=5
DJANGO_SETTINGS_MODULE=timeclock.settings
DJANGO_WSGI_MODULE=timeclock.wsgi

# Activate virtualenv
cd $DJANGODIR
workon timeclock
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
	--name $NAME \
	--workers $NUM_WORKERS \
	#--bind=unix:$SOCKFILE \
	--bind 0.0.0.0:8000
	--log-leve=debug \
	--log-file=-
