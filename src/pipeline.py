from .aggregate import build_gold
from .ingest import load_or_fetch_bronze
from .transform import build_silver


def run_pipeline(refresh=False):
    """Run Bronze -> Silver -> Gold voor de RWS-waterstandpipeline."""
    bronze = load_or_fetch_bronze(refresh=refresh)
    silver = build_silver(bronze)
    gold = build_gold(silver)
    return {"bronze_rows": len(bronze), "silver_rows": len(silver), "gold": gold}


if __name__ == "__main__":
    result = run_pipeline()
    print({key: value for key, value in result.items() if key != "gold"})
