import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_page_calculator.settings')

app = Celery('django_page_calculator')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# celery beat tasks

app.conf.beat_schedule = {
    'check-files-in-db-and-in-storage': {
        'task': 'print_service_app.tasks.delete_files',
        'schedule': crontab(day_of_week='sunday', minute=0, hour=2)
    }
}
