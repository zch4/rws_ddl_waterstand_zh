# Data

De databestanden worden niet meegeleverd in deze repository.

De notebook en scripts halen de waterstandsdata op uit RWS DDL via `ddlpy` en
schrijven lokaal Parquet-bestanden weg naar deze map.

Belangrijke lokale bestanden die opnieuw kunnen worden aangemaakt:

- `data/bronze/rws_waterstand_zh_2022_2025.parquet`
- `data/bronze/meetstations.parquet`
- `data/bronze/astronomische_waterhoogte_zh_2022_2025.parquet`
- `data/silver/waterstand_silver_2022_2025.parquet`
- `data/gold/waterstand_daggemiddeld_2022_2025.parquet`
- `data/gold/waterstand_maandgemiddeld_2022_2025.parquet`
- `data/gold/waterstand_seizoen_2022_2025.parquet`

Run de notebook om alle bestanden lokaal opnieuw aan te maken. De scripts in
`src/` kunnen de gemeten waterstanden verwerken; de notebook bevat daarnaast
ook de stap voor astronomische waterhoogte.
