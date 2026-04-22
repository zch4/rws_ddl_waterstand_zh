"""Data service voor het Waterstand Zuid-Holland dashboard.

De Django-app leest de Parquet-bestanden uit het waterstand-project en maakt
kleine datasets voor de grafieken. 
"""
from functools import lru_cache
from pathlib import Path

import pandas as pd
from django.conf import settings


grafiek_kleuren = [
    "#20808D",
    "#A84B2F",
    "#1B474D",
    "#944454",
    "#FFC553",
    "#848456",
    "#5B8DB8",
    "#7B5EA7",
]

meetstations_volgorde = [
    "Scheveningen",
    "Hoek van Holland",
    "Vlaardingen",
    "Rotterdam",
    "Spijkenisse",
    "Dordrecht",
    "Krimpen a/d IJssel",
    "Gouda",
]

meetstations_kleuren = dict(zip(meetstations_volgorde, grafiek_kleuren))

maanden_list = [
    "jan", "feb", "mrt", "apr", "mei", "jun",
    "jul", "aug", "sep", "okt", "nov", "dec",
]


def _waterstand_data_dir() -> Path:
    """Bepaal waar de waterstanddata staat."""
    default = settings.BASE_DIR.parent / "data"
    return Path(getattr(settings, "WATERSTAND_DATA_DIR", default))


def _lees_parquet(relatief_pad: str) -> pd.DataFrame:
    pad = _waterstand_data_dir() / relatief_pad
    if not pad.exists():
        raise FileNotFoundError(f"Waterstanddata niet gevonden: {pad}")
    return pd.read_parquet(pad)


@lru_cache(maxsize=1)
def laad_silver_data() -> pd.DataFrame:
    """Laad opgeschoonde 10-minutenmetingen."""
    silver_data = _lees_parquet("silver/waterstand_silver_2022_2025.parquet")
    silver_data["tijdstip"] = pd.to_datetime(silver_data["tijdstip"])
    silver_data["datum"] = pd.to_datetime(silver_data["datum"])
    return silver_data


@lru_cache(maxsize=1)
def laad_gold_dag() -> pd.DataFrame:
    """Laad daggemiddelden per meetstation."""
    gold_dag = _lees_parquet("gold/waterstand_daggemiddeld_2022_2025.parquet")
    gold_dag["datum"] = pd.to_datetime(gold_dag["datum"])
    return gold_dag


@lru_cache(maxsize=1)
def laad_astro_dag() -> pd.DataFrame:
    """Laad astronomische waterhoogte en maak daggemiddelden."""
    astro = _lees_parquet("bronze/astronomische_waterhoogte_zh_2022_2025.parquet")
    astro["tijdstip"] = pd.to_datetime(astro["tijdstip"])
    astro["datum"] = astro["tijdstip"].dt.date
    astro["waterhoogte_cm"] = pd.to_numeric(
        astro["Meetwaarde.Waarde_Numeriek"], errors="coerce"
    )
    astro_dag = (
        astro.dropna(subset=["waterhoogte_cm"])
        .groupby(["meetstation_code", "meetstation_naam", "datum"], as_index=False)
        .agg(gemiddelde=("waterhoogte_cm", "mean"), n_metingen=("waterhoogte_cm", "size"))
    )
    astro_dag = astro_dag[astro_dag["n_metingen"] >= 100].copy()
    astro_dag["datum"] = pd.to_datetime(astro_dag["datum"])
    return astro_dag


def _station_volgorde() -> list[str]:
    gold_dag = laad_gold_dag()
    namen = sorted(gold_dag["meetstation_naam"].unique().tolist())
    return [naam for naam in meetstations_volgorde if naam in namen] + [
        naam for naam in namen if naam not in meetstations_volgorde
    ]


def _kleur(naam: str) -> str:
    return meetstations_kleuren.get(naam, "#20808D")


def _labels_datums(datums: pd.Series) -> list[str]:
    return pd.to_datetime(datums).dt.strftime("%Y-%m-%d").tolist()


def get_stations() -> list[dict]:
    """Stations voor sidebar en overzichtstabel."""
    silver_data = laad_silver_data()
    stations = []
    for naam in _station_volgorde():
        subset = silver_data[silver_data["meetstation_naam"] == naam]
        if subset.empty:
            continue
        stations.append(
            {
                "naam": naam,
                "code": subset["meetstation_code"].iloc[0],
                "kleur": _kleur(naam),
                "n_metingen": len(subset),
                "gemiddelde_cm": round(float(subset["waterstand_cm"].mean()), 1),
                "p95_cm": round(float(subset["waterstand_cm"].quantile(0.95)), 1),
            }
        )
    return stations


def get_overzicht_stats() -> dict:
    """KPI-kaarten voor de dashboard-header."""
    silver_data = laad_silver_data()
    hoogste_maand = (
        silver_data.groupby("maand")["waterstand_cm"].mean().sort_values(ascending=False)
    )
    maand_nr = int(hoogste_maand.index[0])
    return {
        "totaal_metingen": len(silver_data),
        "aantal_stations": silver_data["meetstation_naam"].nunique(),
        "periode_start": int(silver_data["jaar"].min()),
        "periode_eind": int(silver_data["jaar"].max()),
        "gemiddelde_cm": round(float(silver_data["waterstand_cm"].mean()), 1),
        "hoogste_maand": maanden_list[maand_nr - 1],
    }


def _weekgemiddelden(df: pd.DataFrame) -> pd.DataFrame:
    """Maak weekgemiddelden voor snellere dashboardgrafieken."""
    week = df.copy()
    week["week_start"] = week["datum"].dt.to_period("W").dt.start_time
    return (
        week.groupby(["meetstation_code", "meetstation_naam", "week_start"], as_index=False)
        .agg(gemiddelde=("gemiddelde", "mean"))
        .rename(columns={"week_start": "datum"})
    )


def get_gold_dag() -> dict:
    """Gemeten waterstand per station, als weekgemiddelde voor het dashboard."""
    gold_dag = _weekgemiddelden(laad_gold_dag())
    datums = sorted(gold_dag["datum"].unique())
    labels = pd.Series(datums).dt.strftime("%Y-%m-%d").tolist()
    datasets = []
    for naam in _station_volgorde():
        subset = gold_dag[gold_dag["meetstation_naam"] == naam].set_index("datum")
        waarden = subset.reindex(datums)["gemiddelde"].round(1)
        datasets.append(
            {
                "label": naam,
                "kleur": _kleur(naam),
                "waarden": [None if pd.isna(v) else float(v) for v in waarden],
            }
        )
    return {
        "labels": labels,
        "datasets": datasets,
        "eenheid": "cm t.o.v. NAP",
        "resolutie": "weekgemiddelde",
    }


def get_astro_dag() -> dict:
    """Astronomische waterhoogte per station, als weekgemiddelde."""
    astro_dag = _weekgemiddelden(laad_astro_dag())
    datums = sorted(astro_dag["datum"].unique())
    labels = pd.Series(datums).dt.strftime("%Y-%m-%d").tolist()
    datasets = []
    for naam in _station_volgorde():
        subset = astro_dag[astro_dag["meetstation_naam"] == naam].set_index("datum")
        waarden = subset.reindex(datums)["gemiddelde"].round(1)
        datasets.append(
            {
                "label": naam,
                "kleur": _kleur(naam),
                "waarden": [None if pd.isna(v) else float(v) for v in waarden],
            }
        )
    return {
        "labels": labels,
        "datasets": datasets,
        "eenheid": "cm t.o.v. NAP",
        "resolutie": "weekgemiddelde",
    }


def get_maandpatroon() -> dict:
    """Gemiddelde gemeten waterstand per maand, alle jaren gecombineerd."""
    silver_data = laad_silver_data()
    datasets = []
    for naam in _station_volgorde():
        subset = silver_data[silver_data["meetstation_naam"] == naam]
        maand_gem = subset.groupby("maand")["waterstand_cm"].mean()
        waarden = [
            None if pd.isna(maand_gem.get(m)) else round(float(maand_gem.get(m)), 1)
            for m in range(1, 13)
        ]
        datasets.append({"label": naam, "kleur": _kleur(naam), "waarden": waarden})
    return {"labels": maanden_list, "datasets": datasets, "eenheid": "cm t.o.v. NAP"}


def get_extremen_maand() -> dict:
    """Aantal metingen boven de eigen P95-drempel per maand."""
    silver_data = laad_silver_data()
    p95 = silver_data.groupby("meetstation_naam")["waterstand_cm"].quantile(0.95)
    extremen = silver_data.join(p95.rename("p95"), on="meetstation_naam")
    extremen = extremen[extremen["waterstand_cm"] > extremen["p95"]]
    datasets = []
    for naam in _station_volgorde():
        subset = extremen[extremen["meetstation_naam"] == naam]
        aantallen = subset.groupby("maand").size()
        waarden = [int(aantallen.get(m, 0)) for m in range(1, 13)]
        datasets.append({"label": naam, "kleur": _kleur(naam), "waarden": waarden})
    return {"labels": maanden_list, "datasets": datasets, "eenheid": "metingen"}


def get_gem_loc() -> dict:
    """Locaties van meetstations met gemiddelde waterstand."""
    silver_data = laad_silver_data()
    stations = []
    for naam in _station_volgorde():
        subset = silver_data[silver_data["meetstation_naam"] == naam]
        if subset.empty:
            continue
        stations.append(
            {
                "naam": naam,
                "code": subset["meetstation_code"].iloc[0],
                "kleur": _kleur(naam),
                "lat": round(float(subset["lat"].iloc[0]), 6),
                "lon": round(float(subset["lon"].iloc[0]), 6),
                "gemiddelde_cm": round(float(subset["waterstand_cm"].mean()), 1),
            }
        )
    return {"stations": stations, "eenheid": "cm t.o.v. NAP"}


def get_uurprofiel_hvh() -> dict:
    """Gemiddeld uurprofiel voor Hoek van Holland, zoals in het notebook."""
    silver_data = laad_silver_data()
    subset = silver_data[silver_data["meetstation_naam"] == "Hoek van Holland"]
    if subset.empty:
        return {"labels": [], "waarden": [], "eenheid": "cm t.o.v. NAP"}

    uurprofiel = subset.groupby("uur")["waterstand_cm"].mean()
    labels = [f"{uur_nr:02d}:00" for uur_nr in range(24)]
    waarden = [
        None if pd.isna(uurprofiel.get(uur_nr)) else round(float(uurprofiel.get(uur_nr)), 1)
        for uur_nr in range(24)
    ]
    return {"labels": labels, "waarden": waarden, "eenheid": "cm t.o.v. NAP"}
