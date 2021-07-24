#!/usr/bin/bash
python manage.py migrate
python manage.py loaddata $1