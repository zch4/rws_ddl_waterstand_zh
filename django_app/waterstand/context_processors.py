"""
Context processors: globale template-variabelen voor navigatie.
"""
from .data_service import get_stations


def sidebar_context(request):
    """Laad alle stations voor de sidebar-navigatie."""
    resolver_match = getattr(request, "resolver_match", None)
    kwargs = getattr(resolver_match, "kwargs", {}) if resolver_match else {}
    return {
        "alle_stations": get_stations(),
        "actieve_station_code": kwargs.get("station_code", ""),
    }
