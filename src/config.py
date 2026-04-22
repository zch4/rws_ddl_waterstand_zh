from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"
GOLD_DIR = BASE_DIR / "data" / "gold"
PLOTS_DIR = BASE_DIR / "plots"

for directory in [BRONZE_DIR, SILVER_DIR, GOLD_DIR, PLOTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

MEETSTATIONS_SELECTIE = {
    "hoekvanholland": "Hoek van Holland",
    "scheveningen": "Scheveningen",
    "vlaardingen": "Vlaardingen",
    "rotterdam.nieuwemaas.boerengat": "Rotterdam",
    "spijkenisse.oudemaas": "Spijkenisse",
    "dordrecht.oudemaas.benedenmerwede": "Dordrecht",
    "krimpenaandeijssel.hollandscheijssel": "Krimpen a/d IJssel",
    "gouda.hollandscheijssel": "Gouda",
}

MEETSTATION_CODES = list(MEETSTATIONS_SELECTIE)
JAARTALLEN = [2022, 2023, 2024, 2025]
START_DATUM = "2022-01-01"
EIND_DATUM = "2025-12-31"

MEETSTATIONS_FILE = BRONZE_DIR / "meetstations.parquet"
BRONZE_FILE = BRONZE_DIR / "rws_waterstand_zh_2022_2025.parquet"
SILVER_FILE = SILVER_DIR / "waterstand_silver_2022_2025.parquet"
