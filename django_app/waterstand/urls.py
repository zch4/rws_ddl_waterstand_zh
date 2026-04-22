"""URL-routes voor de Waterstand Zuid-Holland app."""
from django.urls import path
from . import views

app_name = "waterstand"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),

    # JSON API-endpoints voor de vijf visualisaties
    path("api/daggemiddelden/", views.api_daggemiddelden, name="api_daggemiddelden"),
    path("api/astronomisch/", views.api_astronomisch, name="api_astronomisch"),
    path("api/seizoen/", views.api_seizoen, name="api_seizoen"),
    path("api/extremen/", views.api_extremen, name="api_extremen"),
    path("api/uurprofiel/", views.api_uurprofiel, name="api_uurprofiel"),
    path("api/stationkaart/", views.api_stationkaart, name="api_stationkaart"),
]
