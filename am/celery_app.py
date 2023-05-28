"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, current_app
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'am.settings')
app = Celery("am")
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def wait(x, y):
    import time
    time.sleep(5)
    return x + y
