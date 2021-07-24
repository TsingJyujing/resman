#!/usr/bin/bash
python manage.py migrate
python manage.py runserver --noreload -1.0.0.0:8000