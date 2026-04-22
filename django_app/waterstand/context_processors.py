"""
Context processors: globale template-variabelen voor navigatie.
"""
from .data_service import get_stations


def sidebar_context(request):
    """Laad stations voor globale template-variabelen als data beschikbaar is."""
    resolver_match = getattr(request, "resolver_match", None)
    kwargs = getattr(resolver_match, "kwargs", {}) if resolver_match else {}
    try:
        stations = get_stations()
    except FileNotFoundError:
        stations = []
    return {
        "alle_stations": stations,
        "actieve_station_code": kwargs.get("station_code", ""),
    }
