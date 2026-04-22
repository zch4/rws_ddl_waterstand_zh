import pandas as pd

from .config import GOLD_DIR


def build_gold(silver_data: pd.DataFrame, output_dir=GOLD_DIR) -> dict[str, pd.DataFrame]:
    """Maak Gold-tabellen voor analyse en dashboard."""
    gold_dag = (
        silver_data.groupby(["meetstation_code", "meetstation_naam", "lat", "lon", "datum"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
            n_metingen=("waterstand_cm", "count"),
        )
        .reset_index()
    )
    gold_dag["datum"] = pd.to_datetime(gold_dag["datum"])
    gold_dag["maand"] = gold_dag["datum"].dt.month

    gold_maand = (
        silver_data.groupby(["meetstation_code", "meetstation_naam", "jaar", "maand"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
        )
        .reset_index()
    )

    gold_seizoen = (
        silver_data.groupby(["meetstation_code", "meetstation_naam", "seizoen"])
        .agg(
            gemiddelde=("waterstand_cm", "mean"),
            minimum=("waterstand_cm", "min"),
            maximum=("waterstand_cm", "max"),
        )
        .reset_index()
    )

    outputs = {
        "waterstand_daggemiddeld_2022_2025.parquet": gold_dag,
        "waterstand_maandgemiddeld_2022_2025.parquet": gold_maand,
        "waterstand_seizoen_2022_2025.parquet": gold_seizoen,
    }
    for naam, frame in outputs.items():
        frame.to_parquet(output_dir / naam, index=False)
    return outputs
