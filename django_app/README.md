# Waterstand ZH - eenvoudig Django-dashboard

Deze Django-app maakt de waterstand-analyse uit het notebook interactief
bekijkbaar. De app is bewust eenvoudig gehouden: een pagina met dezelfde vijf
visualisaties als het notebook.

## Wat toont de app?

- Visualisatie 1a: gemeten waterstand per meetstation.
- Visualisatie 1b: astronomische waterhoogte als getijreferentie.
- Visualisatie 2: gemiddeld maandpatroon.
- Visualisatie 3: hoge-watermomenten boven de P95-drempel.
- Visualisatie 4: gemiddeld uurprofiel voor Hoek van Holland.
- Visualisatie 5: eenvoudige kaart met de meetstations.

## Technische opzet

```text
../data/*.parquet -> pandas in data_service.py -> Django views -> JSON API -> Chart.js
```

De belangrijkste bestanden zijn:

- `waterstand/data_service.py`: leest de data en maakt kleine aggregaties.
- `waterstand/views.py`: toont de dashboardpagina en levert JSON-data.
- `waterstand/templates/waterstand/dashboard.html`: bevat de pagina-indeling.
- `waterstand/static/waterstand/js/dashboard.js`: tekent de grafieken.
- `waterstand/static/waterstand/css/style.css`: bevat de eenvoudige opmaak.

De namen in `data_service.py` sluiten aan op het notebook, bijvoorbeeld
`silver_data`, `gold_dag`, `astro_dag`, `maandpatroon`, `extremen`,
`meetstations_volgorde` en `meetstations_kleuren`.

## Lokaal draaien

Draai eerst de notebook in de repo-root, zodat de benodigde Parquet-bestanden in
`../data/` bestaan.

Gebruik de virtual environment uit de portfolio-root:

```powershell
cd "C:\Users\zizha\Desktop\data-engineering\Nelen & Schuurmans"
.\.venv\Scripts\Activate.ps1
cd ".\rws_ddl_waterstand_zh\django_app"
python manage.py check
python manage.py runserver
```

Open daarna:

```text
http://127.0.0.1:8000/
```

## Checks

```powershell
python manage.py check
python manage.py test
```

## Portfolio-uitleg

De notebook is het hoofdproject. Deze Django-app is een eenvoudige
presentatielaag bovenop dezelfde data. Django, HTML en JavaScript zijn hierbij
vooral gebruikt om de resultaten interactief te tonen.
