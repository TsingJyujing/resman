#!/bin/sh
# Initializing script for dev
# Waiting for DB prepared
until python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);r=s.connect_ex(('db',5432));s.close();exit(r)"
do
  echo "Waiting for DB..."
  sleep 1
done
python manage.py migrate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('$ADMIN_NAME', 'resman-admin@tsingjyujing.com', '$ADMIN_PASSWORD')" | python manage.py shell | true
exec "$@"