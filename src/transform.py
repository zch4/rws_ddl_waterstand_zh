import pandas as pd

from .config import SILVER_FILE

VALID_QUALITY_CODES = {"00", "10", "20", "25"}


def _seizoen(maand: int) -> str:
    if maand in (12, 1, 2):
        return "Winter"
    if maand in (3, 4, 5):
        return "Lente"
    if maand in (6, 7, 8):
        return "Zomer"
    return "Herfst"


def build_silver(bronze_data: pd.DataFrame, output_path=SILVER_FILE) -> pd.DataFrame:
    """Schoon ruwe RWS-metingen op en voeg tijdskenmerken toe."""
    silver_data = bronze_data.copy()
    silver_data["tijdstip"] = pd.to_datetime(silver_data["tijdstip"])
    silver_data["waterstand_cm"] = pd.to_numeric(
        silver_data["Meetwaarde.Waarde_Numeriek"], errors="coerce"
    )
    silver_data["kwaliteit"] = (
        silver_data["WaarnemingMetadata.Kwaliteitswaardecode"].astype(str).str.strip()
    )

    silver_data = silver_data.dropna(subset=["tijdstip", "waterstand_cm"])
    silver_data = silver_data[silver_data["waterstand_cm"] > -9999]
    silver_data = silver_data[silver_data["kwaliteit"].isin(VALID_QUALITY_CODES)]

    silver_data["datum"] = silver_data["tijdstip"].dt.date
    silver_data["jaar"] = silver_data["tijdstip"].dt.year
    silver_data["maand"] = silver_data["tijdstip"].dt.month
    silver_data["dag"] = silver_data["tijdstip"].dt.day
    silver_data["uur"] = silver_data["tijdstip"].dt.hour
    silver_data["seizoen"] = silver_data["maand"].map(_seizoen)

    kolommen = [
        "tijdstip",
        "datum",
        "meetstation_code",
        "meetstation_naam",
        "lat",
        "lon",
        "waterstand_cm",
        "jaar",
        "maand",
        "dag",
        "uur",
        "seizoen",
    ]
    silver_data = silver_data[kolommen].reset_index(drop=True)
    silver_data.to_parquet(output_path, index=False)
    return silver_data
