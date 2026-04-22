"""Eenvoudige Prefect-flow voor de waterstand-pipeline.

Deze flow sluit aan op de notebookversie van het project. De Bronze-data is al
opgehaald uit RWS DDL; Prefect orkestreert hier de stappen Bronze -> Silver ->
Gold en schrijft de Parquet-bestanden opnieuw weg.
"""
from pathlib import Path
import os

import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parents[1]
PREFECT_HOME = PROJECT_DIR / ".prefect"
PREFECT_HOME.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("PREFECT_HOME", str(PREFECT_HOME))
os.environ.setdefault("DO_NOT_TRACK", "1")
os.environ.setdefault("PREFECT_SERVER_ANALYTICS_ENABLED", "false")

from prefect import flow, get_run_logger, task

BRONZE_FILE = PROJECT_DIR / "data" / "bronze" / "rws_waterstand_zh_2022_2025.parquet"
SILVER_FILE = PROJECT_DIR / "data" / "silver" / "waterstand_silver_2022_2025.parquet"
GOLD_DIR = PROJECT_DIR / "data" / "gold"

VALID_QUALITY_CODES = {"00", "10", "20", "25"}


def _seizoen(maand: int) -> str:
    if maand in (12, 1, 2):
        return "Winter"
    if maand in (3, 4, 5):
        return "Lente"
    if maand in (6, 7, 8):
        return "Zomer"
    return "Herfst"


@task(retries=2, retry_delay_seconds=10)
def laad_bronze(bronze_file: Path = BRONZE_FILE) -> pd.DataFrame:
    """Laad de ruwe waterstandsmetingen uit de Bronze-laag."""
    logger = get_run_logger()
    if not bronze_file.exists():
        raise FileNotFoundError(f"Bronze-bestand niet gevonden: {bronze_file}")

    bronze = pd.read_parquet(bronze_file)
    logger.info("Bronze geladen: %s records", len(bronze))
    return bronze


@task
def maak_silver(bronze: pd.DataFrame, silver_file: Path = SILVER_FILE) -> pd.DataFrame:
    """Schoon ruwe metingen op en voeg tijdskenmerken toe."""
    logger = get_run_logger()
    silver = bronze.copy()

    silver["tijdstip"] = pd.to_datetime(silver["tijdstip"])
    silver["waterstand_cm"] = pd.to_numeric(
        silver["Meetwaarde.Waarde_Numeriek"], errors="coerce"
    )
    silver["kwaliteit"] = (
        silver["WaarnemingMetadata.Kwaliteitswaardecode"].astype(str).str.strip()
    )

    silver = silver.dropna(subset=["tijdstip", "waterstand_cm"])
    silver = silver[silver["waterstand_cm"] > -9999]
    silver = silver[silver["kwaliteit"].isin(VALID_QUALITY_CODES)]

    silver["datum"] = silver["tijdstip"].dt.date
    silver["jaar"] = silver["tijdstip"].dt.year
    silver["maand"] = silver["tijdstip"].dt.month
    silver["dag"] = silver["tijdstip"].dt.day
    silver["uur"] = silver["tijdstip"].dt.hour
    silver["seizoen"] = silver["maand"].map(_seizoen)

    kolommen = [
        "tijdstip",
        "datum",
        "meetstation_code",
        "meetstation_naam",
        "Lat",
        "Lon",
        "waterstand_cm",
        "jaar",
        "maand",
        "dag",
        "uur",
        "seizoen",
    ]
    silver = silver[kolommen].rename(columns={"Lat": "lat", "Lon": "lon"})
    silver_file.parent.mkdir(parents=True, exist_ok=True)
    silver.to_parquet(silver_file, index=False)

    logger.info("Silver geschreven: %s records -> %s", len(silver), silver_file)
    return silver


@task
def maak_gold(silver: pd.DataFrame, gold_dir: Path = GOLD_DIR) -> dict[str, int]:
    """Maak dag-, maand- en seizoentabellen voor analyse en dashboard."""
    logger = get_run_logger()
    gold_dir.mkdir(parents=True, exist_ok=True)

    dag = (
        silver.groupby(["meetstation_code", "meetstation_naam", "lat", "lon", "datum"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
            n_metingen=("waterstand_cm", "count"),
        )
        .reset_index()
    )
    dag["datum"] = pd.to_datetime(dag["datum"])
    dag["maand"] = dag["datum"].dt.month

    maand = (
        silver.groupby(["meetstation_code", "meetstation_naam", "jaar", "maand"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
        )
        .reset_index()
    )

    seizoen = (
        silver.groupby(["meetstation_code", "meetstation_naam", "seizoen"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
        )
        .reset_index()
    )

    dag.to_parquet(gold_dir / "waterstand_daggemiddeld_2022_2025.parquet", index=False)
    maand.to_parquet(gold_dir / "waterstand_maandgemiddeld_2022_2025.parquet", index=False)
    seizoen.to_parquet(gold_dir / "waterstand_seizoen_2022_2025.parquet", index=False)

    logger.info("Gold geschreven: dag=%s, maand=%s, seizoen=%s", len(dag), len(maand), len(seizoen))
    return {"dag": len(dag), "maand": len(maand), "seizoen": len(seizoen)}


@flow(name="waterstand-zh-pipeline")
def waterstand_pipeline() -> dict[str, int]:
    """Run Bronze -> Silver -> Gold als eenvoudige Prefect-flow."""
    bronze = laad_bronze()
    silver = maak_silver(bronze)
    gold_counts = maak_gold(silver)
    return {"bronze": len(bronze), "silver": len(silver), **gold_counts}


if __name__ == "__main__":
    resultaat = waterstand_pipeline()
    print(resultaat)
