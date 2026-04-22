# RWS DDL Waterstand Zuid-Holland

## Over dit githubrepo
Dit repo bevat een verkennend open-data project over waterstanden in en rond
Zuid-Holland, gebouwd met open data uit RWS DDL. De pipeline volgt de Medallion
Architecture (bronze → silver → gold) en is gebouwd in Python met Parquet als
opslagformaat.

## Inhoud

In dit repo wordt inzicht gegeven in:
- Gemeten waterstanden van acht meetstations in en rond Zuid-Holland
- Astronomische waterhoogte als getijreferentie
- Seizoenspatronen in gemiddelde waterstanden
- Hoge-watermomenten op basis van P95-drempels
- Gemiddeld uurprofiel van Hoek van Holland
- Ruimtelijke ligging van de geselecteerde meetstations

Notebook:
- [waterstand_zh_pipeline.ipynb](https://github.com/zch4/rws_ddl_waterstand_zh/blob/main/waterstand_zh_pipeline.ipynb)

Daarnaast bevat dit repo een eenvoudige Django-app om dezelfde visualisaties
interactief te bekijken.

## Technologieën
- Python – Dataverwerking (bronze → silver → gold)
- Pandas – Data-analyse, filtering en aggregaties
- ddlpy – Ophalen van RWS DDL-data
- Parquet – Gelaagde dataopslag per fase
- Matplotlib – Visualisaties in het notebook
- Django, Chart.js – Eenvoudige interactieve dashboardweergave
- Prefect – Verkennende pipeline-flow

## Databronnen
- RWS DDL via `ddlpy` – Waterstandsmetingen en astronomische waterhoogte

De ruwe Parquet-bestanden worden niet meegeleverd. De data kan opnieuw worden
opgehaald door het notebook of de pipeline lokaal te draaien.

## Lokaal gebruiken

Installeer de dependencies met:

```powershell
python -m pip install -r requirements.txt
```

Open daarna het notebook:

```powershell
jupyter notebook waterstand_zh_pipeline.ipynb
```

De Django-app gebruikt de lokaal aangemaakte Parquet-bestanden uit `data/`.

## Status
Verkennend open-data project. Het project kan worden uitgebreid met aanvullende
meetstations, langere tijdreeksen, extra hydrologische indicatoren of een
uitgebreidere dashboardomgeving.

Laatst bijgewerkt: april 2026
