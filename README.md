# RWS DDL Waterstand Zuid-Holland

Portfolio-project voor een Junior Data Engineer-sollicitatie bij Nelen &
Schuurmans. Het project verkent waterstanden in en rond Zuid-Holland met open
data uit RWS DDL.

De nadruk ligt op een uitlegbare data-engineering workflow: data ophalen,
opschonen, structureren, aggregeren en visualiseren.

## Wat laat dit project zien?

- Ophalen van open waterstandsdata via `ddlpy`.
- Selectie van acht meetstations van kust naar binnenland.
- Verwerking volgens een Bronze, Silver en Gold structuur.
- Opslag van tussenresultaten als Parquet.
- Analyse van gemeten waterstanden en astronomische waterhoogte.
- Visualisaties van seizoenspatroon, hoge-watermomenten, uurprofiel en
  meetstationlocaties.
- Een eenvoudige Django-dashboarddemo met dezelfde visualisaties als het
  notebook.

## Projectstructuur

```text
rws_ddl_waterstand_zh/
├─ waterstand_zh_pipeline.ipynb
├─ src/
├─ plots/
├─ data/
│  ├─ README.md
│  ├─ bronze/
│  ├─ silver/
│  └─ gold/
└─ django_app/
```

## Data

De Parquet-data staat niet in deze repository. De data kan opnieuw worden
opgehaald uit RWS DDL door de notebook of scripts te draaien.

De belangrijkste bronbestanden die lokaal worden aangemaakt zijn:

- `data/bronze/rws_waterstand_zh_2022_2025.parquet`
- `data/bronze/meetstations.parquet`
- `data/bronze/astronomische_waterhoogte_zh_2022_2025.parquet`

## Notebook draaien

Maak eerst een virtual environment aan en installeer de dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start daarna Jupyter:

```powershell
jupyter notebook waterstand_zh_pipeline.ipynb
```

## Pipeline draaien

De scripts in `src/` laten zien hoe de notebookstappen als herbruikbare
pipeline kunnen worden georganiseerd. De scriptvariant verwerkt de gemeten
waterstanden. Draai de notebook als je ook de astronomische waterhoogte en alle
plots opnieuw wilt maken.

```powershell
python -m src.pipeline
```

Er is ook een eenvoudige Prefect-flow:

```powershell
python -m src.prefect_flow
```

## Django-dashboard draaien

De Django-app gebruikt de lokaal aangemaakte bestanden in `data/`. Draai eerst
de notebook, zodat ook de astronomische waterhoogte beschikbaar is.

```powershell
cd django_app
python manage.py check
python manage.py runserver
```

Open daarna:

```text
http://127.0.0.1:8000/
```

## Visualisaties

De map `plots/` bevat de belangrijkste eindvisualisaties:

- Gemeten waterstand per meetstation.
- Astronomische waterhoogte.
- Seizoenspatroon per maand.
- Hoge-watermomenten boven P95.
- Gemiddeld uurprofiel van Hoek van Holland.
- Locatiekaart van de meetstations.

## Opmerking

Dit is een leer- en portfolio-project. Ik ben geen hydrologisch specialist,
maar heb dit project gemaakt om mijn data-engineeringervaring toe te passen op
een waterbeheercontext.
