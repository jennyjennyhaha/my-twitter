import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'twitter.settings')

app = Celery('twitter')

app.config_from_object('django.conf:settings', namespace='CELERY')

# load task modules from all registered django app configs
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
