 # Note: this import isn't actually used in this file — it belongs in load.py.
# Safe to remove from here unless you're using it directly below.
from sqlalchemy import create_engine

# Core Airflow class used to define a workflow (a "Directed Acyclic Graph")
from airflow import DAG

# Operator that lets a DAG task run a plain Python function
from airflow.operators.python import PythonOperator

# Used to set the DAG's start_date
from datetime import datetime

# sys.path manipulation so Python can find extract.py, transform.py, load.py
# since they live in a different folder than this DAG file
import sys
sys.path.append('Downloads/AI Engineer /Project/ETL/weather-etl/scripts')  # <-- replace with your real path

# Import your three ETL functions from the scripts folder
from extract import extract_weather
from transform import transform_weather
from load import load_weather


def run_pipeline():
    """
    This is the actual ETL logic, wrapped in one function so Airflow
    can call it as a single task. Runs extract -> transform -> load in order.
    """
    raw = extract_weather()          # Step 1: pull raw JSON from the API
    df = transform_weather(raw)      # Step 2: clean it into a DataFrame
    load_weather(df)                 # Step 3: write it into Postgres


# The "with DAG(...) as dag:" block defines the workflow itself —
# its name, schedule, and behavior. Tasks created inside this block
# automatically belong to this DAG.
with DAG(
    "weather_etl",                   # DAG ID — shown in the Airflow UI
    start_date=datetime(2026, 1, 1), # earliest date Airflow considers this DAG "active"
    schedule_interval="@daily",      # run once every day
    catchup=False                    # don't backfill runs for past dates it missed
) as dag:

    # Defines a single task that runs run_pipeline() when triggered
    run_etl = PythonOperator(
        task_id="run_weather_etl",       # unique name for this task within the DAG
        python_callable=run_pipeline     # the function Airflow will execute
    )

    # Since there's only one task, no dependencies (>>) need to be set.
    # If you add more tasks later, you'd chain them like:
    # extract_task >> transform_task >> load_task