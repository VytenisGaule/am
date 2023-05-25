"""
https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
"""
import os

from celery import Celery

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'am.settings')
app = Celery("amscrape")
app.conf.timezone = 'Europe/Vilnius'
app.config_from_object('am.settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task
def divide(x, y):
    import time
    time.sleep(5)
    return x / y


print(app.conf.timezone)
