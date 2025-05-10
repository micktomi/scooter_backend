"""Gunicorn configuration for production environment."""

import multiprocessing
import os

# Βασικές ρυθμίσεις
bind = "0.0.0.0:8000"
worker_class = "uvicorn.workers.UvicornWorker"
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2
timeout = 120

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Εάν υπάρχει ρύθμιση για το Max Requests
max_requests = 1000
max_requests_jitter = 50

# Άλλες ρυθμίσεις
graceful_timeout = 30
keepalive = 5