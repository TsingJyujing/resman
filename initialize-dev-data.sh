#!/usr/bin/env bash
rm -rf db.sqlite3 whoosh_index
mc rm --recursive --force resman_nas/resman/
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
cat create_test_su.py | python3 manage.py shell
