import ddlpy
import pandas as pd

from .config import (
    BRONZE_FILE,
    JAARTALLEN,
    MEETSTATION_CODES,
    MEETSTATIONS_FILE,
    MEETSTATIONS_SELECTIE,
)


def fetch_station_catalog() -> pd.DataFrame:
    """Haal de RWS DDL-catalogus op en selecteer de 8 meetstations."""
    locaties = ddlpy.locations()
    zh_locs = locaties[
        (locaties["Grootheid.Code"] == "WATHTE")
        & (locaties["Compartiment.Code"] == "OW")
        & (locaties["Lat"].between(51.64, 52.34))
        & (locaties["Lon"].between(3.84, 5.04))
        & (
            locaties["Parameter_Wat_Omschrijving"]
            .fillna("")
            .str.contains("Normaal Amsterdams Peil", na=False)
        )
        & (
            ~locaties["Parameter_Wat_Omschrijving"]
            .fillna("")
            .str.contains("astronomisch|verwachting", case=False, na=False)
        )
    ].copy()
    zh_locs = zh_locs[~zh_locs.index.duplicated(keep="first")]

    meetstations = zh_locs.loc[MEETSTATION_CODES].copy()
    meetstations["portfolio_naam"] = meetstations.index.map(MEETSTATIONS_SELECTIE)
    meetstations[
        ["Naam", "portfolio_naam", "Lat", "Lon", "Parameter_Wat_Omschrijving"]
    ].to_parquet(MEETSTATIONS_FILE)
    return meetstations


def fetch_water_levels(meetstations: pd.DataFrame | None = None) -> pd.DataFrame:
    """Haal 10-minutenmetingen per meetstation en jaar op uit RWS DDL."""
    meetstations = meetstations if meetstations is not None else fetch_station_catalog()
    delen = []

    for code, naam in MEETSTATIONS_SELECTIE.items():
        locatie = meetstations.loc[code]
        for jaar in JAARTALLEN:
            deel = ddlpy.measurements(
                locatie,
                start_date=f"{jaar}-01-01",
                end_date=f"{jaar}-12-31",
            )
            if deel.empty:
                continue
            deel["meetstation_code"] = code
            deel["meetstation_naam"] = naam
            deel["lat"] = locatie["Lat"]
            deel["lon"] = locatie["Lon"]
            delen.append(deel)

    if not delen:
        return pd.DataFrame()
    return pd.concat(delen).reset_index(names="tijdstip")


def load_or_fetch_bronze(path=BRONZE_FILE, refresh=False) -> pd.DataFrame:
    """Laad Bronze-data uit cache of haal deze opnieuw op uit RWS DDL."""
    if path.exists() and not refresh:
        return pd.read_parquet(path)

    meetstations = fetch_station_catalog()
    bronze_data = fetch_water_levels(meetstations)
    bronze_data.to_parquet(path, index=False)
    return bronze_data
