import os

bind = "0.0.0.0:8000"
worker_class = "sync"
workers = int(os.getenv("DJANGO_WORKERS", "2"))
preload = True
