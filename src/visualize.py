import matplotlib.pyplot as plt
import pandas as pd

from .config import PLOTS_DIR


def plot_daily_levels(daily: pd.DataFrame, output_path=PLOTS_DIR / "vis1_daggemiddelden.png"):
    """Create the main daily average water-level plot."""
    fig, ax = plt.subplots(figsize=(13, 5))
    for _, group in daily.groupby("station_code"):
        group = group.sort_values("datum")
        ax.plot(group["datum"], group["gemiddelde"], linewidth=0.8, label=group["station_naam"].iloc[0])
    ax.axhline(0, color="0.3", linewidth=0.8, linestyle="--", label="NAP (0 m)")
    ax.set_title("Daggemiddelde waterstand - Zuid-Holland (2023-2025)")
    ax.set_ylabel("Waterstand (m t.o.v. NAP)")
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig, ax


def plot_station_map(
    stations: pd.DataFrame,
    output_path=PLOTS_DIR / "vis5_kaart.png",
    value_column: str = "gem_waterstand",
):
    """Plot station locations with optional Zuid-Holland boundaries.

    The map keeps municipality boundaries subtle and uses the province outline
    as the main geographic reference. If PDOK is unavailable, the station plot
    still renders without administrative boundaries.
    """
    from io import BytesIO

    import geopandas as gpd
    import requests

    gdf = gpd.GeoDataFrame(
        stations,
        geometry=gpd.points_from_xy(stations["Lon"], stations["Lat"]),
        crs="EPSG:4326",
    )

    province = None
    municipalities = None
    try:
        base_url = "https://service.pdok.nl/cbs/gebiedsindelingen/2024/wfs/v1_0"
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "outputFormat": "application/json",
        }

        province_resp = requests.get(
            base_url,
            params={
                **params,
                "typeName": "gebiedsindelingen:provincie_gegeneraliseerd",
                "CQL_FILTER": "statcode='PV28'",
            },
            timeout=30,
        )
        province_resp.raise_for_status()
        province = gpd.read_file(BytesIO(province_resp.content)).to_crs("EPSG:4326")
        if "statcode" in province.columns:
            province = province[province["statcode"] == "PV28"].copy()

        municipality_resp = requests.get(
            base_url,
            params={**params, "typeName": "gebiedsindelingen:gemeente_gegeneraliseerd"},
            timeout=30,
        )
        municipality_resp.raise_for_status()
        all_municipalities = gpd.read_file(BytesIO(municipality_resp.content)).to_crs("EPSG:4326")
        municipalities = gpd.clip(all_municipalities, province)
    except Exception:
        province = None
        municipalities = None

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor("#D8ECF3")

    if province is not None and not province.empty:
        province.plot(ax=ax, color="#EAF4ED", edgecolor="#244B42", linewidth=1.4, alpha=0.95)
        if municipalities is not None and not municipalities.empty:
            municipalities.boundary.plot(ax=ax, color="#8AA39A", linewidth=0.35, alpha=0.45)

    scatter = ax.scatter(
        gdf["Lon"],
        gdf["Lat"],
        c=gdf[value_column],
        cmap="RdYlBu",
        s=155,
        zorder=5,
        edgecolors="#222222",
        linewidth=0.8,
    )
    fig.colorbar(scatter, ax=ax, label="Gemiddelde waterstand (m t.o.v. NAP)", shrink=0.62)

    for _, row in gdf.iterrows():
        label = row.get("portfolio_naam") or row.get("station_naam") or row.get("Naam") or row.get("station_code")
        ax.annotate(
            label,
            (row["Lon"], row["Lat"]),
            xytext=(6, 5),
            textcoords="offset points",
            fontsize=8,
            color="#1F2D2A",
        )

    if province is not None and not province.empty:
        minx, miny, maxx, maxy = province.total_bounds
    else:
        minx, miny, maxx, maxy = gdf.total_bounds
    ax.set_xlim(minx - 0.08, maxx + 0.22)
    ax.set_ylim(miny - 0.05, maxy + 0.05)
    ax.set_title("Meetstations waterstand - Zuid-Holland", fontsize=13, pad=12)
    ax.set_xlabel("Lengtegraad")
    ax.set_ylabel("Breedtegraad")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    return fig, ax
