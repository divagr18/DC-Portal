# portalDC/urls.py
from django.contrib import admin
from django.urls import path, include # Make sure include is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    path('submissions/', include('submissions.urls')), # Include submissions app URLs
]