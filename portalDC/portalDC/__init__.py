# portal_project/__init__.py

# Import the Celery app instance defined in celery.py
from .celery import app as celery_app

# Make sure the app is always imported when Django starts
__all__ = ('celery_app',)