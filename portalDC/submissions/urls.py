# submissions/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_assignment_view, name='submit_assignment'),
    path('status/<int:pk>/', views.submission_status_view, name='submission_status'),

]