from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Setting the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MetaSqueeze.settings')

app = Celery('MetaSqueeze')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks from all registered Django apps.
app.autodiscover_tasks()
