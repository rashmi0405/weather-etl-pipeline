from sqlalchemy import create_engine  # SQLAlchemy gives us a clean way to talk to Postgres from pandas

def load_weather(df, table_name="weather_data"):
    # Create a connection "engine" to the local weather_db database
    # Format: postgresql://user:password@host/database — since there's no
    # user/password here, it uses your current system username with no password
    engine = create_engine("postgresql://localhost/weather_db")

    # Write the dataframe to a Postgres table
    # if_exists="replace" -> drops and recreates the table each run (fine for learning/dev,
    #   but in production you'd usually use "append" so you don't lose history)
    # index=False -> don't write pandas' row index (0,1,2...) as its own column
    df.to_sql(table_name, engine, if_exists="append", index=False)

    # Simple confirmation so you know the load step actually ran and how much data moved
    print(f"Loaded {len(df)} rows into {table_name}")

# This block only runs when you execute load.py directly (python load.py)
# — it won't run if this file is imported by something else, like the Airflow DAG
if __name__ == "__main__":
    # Import here (not at the top) so this file can still be imported elsewhere
    # without requiring extract.py/transform.py to exist in the same run context
    from extract import extract_weather
    from transform import transform_weather

    raw = extract_weather()        # Step 1: pull raw JSON from the API
    df = transform_weather(raw)    # Step 2: clean it into a tidy dataframe
    load_weather(df)               # Step 3: push it into Postgres