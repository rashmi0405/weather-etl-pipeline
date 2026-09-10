# Weather ETL Pipeline

An automated ETL pipeline that pulls live weather data, cleans it, loads it into PostgreSQL, and visualizes it in an interactive dashboard — orchestrated by Apache Airflow on a daily schedule.

## Architecture

```
Open-Meteo API
      |
      v
+---------------------------------------------+
|              Airflow DAG (daily)             |
|   Extract  -->  Transform  -->  Load         |
+---------------------------------------------+
      |
      v
PostgreSQL (weather_data table)
      |
      v
Streamlit Dashboard (interactive charts + KPIs)
```

## Tech stack

- **Source:** [Open-Meteo API](https://open-meteo.com/) (free, no API key required)
- **Language:** Python (requests, pandas, SQLAlchemy)
- **Orchestration:** Apache Airflow (daily schedule, `@daily`)
- **Storage:** PostgreSQL
- **Visualization:** Streamlit + Plotly

## What it does

1. **Extract** — calls the Open-Meteo API for hourly weather data (temperature, humidity, precipitation) for a given location.
2. **Transform** — cleans the raw JSON into a structured pandas DataFrame: parses timestamps, drops nulls, converts Celsius to Fahrenheit.
3. **Load** — writes the cleaned data into a PostgreSQL table (`weather_data`).
4. **Orchestrate** — Airflow runs the full extract → transform → load sequence automatically once a day, with retry and monitoring built in via the Airflow UI.
5. **Visualize** — a Streamlit dashboard reads directly from Postgres and renders KPIs (avg/max temperature, humidity, total precipitation), a time-series chart, a temperature-vs-humidity comparison, and a precipitation bar chart, all filterable by date range.

## Project structure

```
weather-etl/
├── dags/
│   └── weather_dag.py       # Airflow DAG definition
├── scripts/
│   ├── extract.py           # Pulls raw data from the API
│   ├── transform.py         # Cleans and structures the data
│   └── load.py               # Writes to Postgres
├── dashboard.py               # Streamlit dashboard
└── README.md
```

## How to run it

```bash
# 1. Install dependencies
pip install requests pandas sqlalchemy psycopg2-binary streamlit plotly apache-airflow --break-system-packages

# 2. Create the database
createdb weather_db

# 3. Start Airflow
export AIRFLOW_HOME=~/airflow
airflow db init
airflow webserver -p 8080 &
airflow scheduler &

# 4. Copy dags/weather_dag.py into ~/airflow/dags/
# 5. Trigger the DAG from the Airflow UI at localhost:8080

# 6. Launch the dashboard
streamlit run dashboard.py
```

## Design decisions & trade-offs

- **Load strategy:** the pipeline currently uses `if_exists="replace"` when writing to Postgres — the table is fully rebuilt on each run. This keeps the logic simple for a daily, single-location dataset. A production version would use an upsert/append pattern with deduplication on timestamp to preserve history and avoid rewriting the full table each run.
- **Single location:** hardcoded latitude/longitude for simplicity. This could be parameterized to support multiple cities by adding a `location` dimension table.
- **No data quality checks yet:** the transform step drops nulls but doesn't validate ranges (e.g., a temperature of 200°C would pass through silently). A next iteration would add a validation layer (e.g., Great Expectations or simple assertions) as an Airflow task.
- **Local Postgres, not cloud:** built locally for speed of iteration during learning; the load script uses SQLAlchemy, so swapping in BigQuery or a cloud Postgres instance is a connection-string change, not a rewrite.

## What this demonstrates

- Building a real data pipeline from an external API to a queryable database
- Automating and scheduling data workflows with an industry-standard orchestrator (Airflow)
- Turning raw data into a decision-ready interactive dashboard
- Making and documenting deliberate engineering trade-offs under time constraints
