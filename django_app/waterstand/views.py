"""Views voor het eenvoudige Waterstand Zuid-Holland dashboard."""

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .data_service import (
    get_astro_dag,
    get_extremen_maand,
    get_gem_loc,
    get_gold_dag,
    get_maandpatroon,
    get_overzicht_stats,
    get_stations,
    get_uurprofiel_hvh,
)


class DashboardView(View):
    """Een pagina met de vijf visualisaties uit het notebook."""

    def get(self, request):
        try:
            context = {
                "data_beschikbaar": True,
                "stats": get_overzicht_stats(),
                "stations": get_stations(),
            }
        except FileNotFoundError as exc:
            context = {
                "data_beschikbaar": False,
                "foutmelding": str(exc),
                "stats": None,
                "stations": [],
            }
        return render(request, "waterstand/dashboard.html", context)


def api_daggemiddelden(request):
    """Visualisatie 1a: gemeten waterstand."""
    return JsonResponse(get_gold_dag())


def api_astronomisch(request):
    """Visualisatie 1b: astronomische waterhoogte."""
    return JsonResponse(get_astro_dag())


def api_seizoen(request):
    """Visualisatie 2: maandpatroon."""
    return JsonResponse(get_maandpatroon())


def api_extremen(request):
    """Visualisatie 3: hoge-watermomenten boven P95."""
    return JsonResponse(get_extremen_maand())


def api_uurprofiel(request):
    """Visualisatie 4: gemiddeld uurprofiel Hoek van Holland."""
    return JsonResponse(get_uurprofiel_hvh())


def api_stationkaart(request):
    """Visualisatie 5: ligging van de meetstations."""
    return JsonResponse(get_gem_loc())
