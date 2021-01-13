#!/usr/bin/env bash
rm -rf db.sqlite3 whoosh_index
docker-compose down -v
docker-compose up -d
sleep 20
python3 manage.py makemigrations
python3 manage.py migrate --run-syncdb
cat create_test_su.py | python3 manage.py shell
