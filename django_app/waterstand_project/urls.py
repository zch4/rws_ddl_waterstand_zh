"""URL configuratie voor Waterstand ZH Dashboard."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('waterstand.urls')),
]
