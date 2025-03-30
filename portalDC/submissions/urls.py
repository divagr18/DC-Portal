# submissions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_assignment_view, name='submit_assignment'),
]