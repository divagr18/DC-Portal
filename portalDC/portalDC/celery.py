# portal_project/celery.py
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portalDC.settings')

# Create the Celery application instance
app = Celery('portalDC')

# Load task module settings from Django settings.py.
# Namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps.
# Celery will look for a `tasks.py` file in each app.
app.autodiscover_tasks()

# Optional: Define a sample task here for testing (can be removed later)
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')