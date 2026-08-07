import os

import psycopg2
import psycopg2.extras
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

SOURCE_CONN = dict(
    host=os.environ["SOURCE_DB_HOST"],
    port=int(os.environ["SOURCE_DB_PORT"]),
    dbname=os.environ["SOURCE_DB_NAME"],
    user=os.environ["SOURCE_DB_USER"],
    password=os.environ["SOURCE_DB_PASSWORD"],
)

DWH_CONN = dict(
    host=os.environ["DWH_DB_HOST"],
    port=int(os.environ["DWH_DB_PORT"]),
    dbname=os.environ["DWH_DB_NAME"],
    user=os.environ["DWH_DB_USER"],
    password=os.environ["DWH_DB_PASSWORD"],
)

SOURCE_SYSTEM = "demo_airlines"

CREATE_RAW_TABLE = """
    CREATE SCHEMA IF NOT EXISTS raw;

    drop table if exists raw.airports_data;

    create table raw.airports_data (
        airport_code   character(3) not null,
        airport_name   jsonb        not null,
        city           jsonb        not null,
        country        jsonb        not null,
        coordinates    point        not null,
        timezone       text         not null,
        _loaded_at     timestamptz  not null,
        _source_system text         not null
    );
"""

EXTRACT_SQL = """
    SELECT
        airport_code,
        airport_name::text AS airport_name,
        city::text AS city,
        country::text AS country,
        coordinates::text AS coordinates,
        timezone
    FROM bookings.airports_data
"""

INSERT_SQL = """
    INSERT INTO raw.airports_data (
        airport_code, airport_name, city, country, coordinates, timezone,
        _loaded_at, _source_system
    ) VALUES %s
"""

INSERT_TEMPLATE = "(%s, %s::jsonb, %s::jsonb, %s::jsonb, %s::point, %s, %s, %s)"


def extract(source_conn):
    """Читает все строки исходной таблицы. Возвращает список кортежей."""
    with source_conn.cursor() as cur:
        cur.execute(EXTRACT_SQL)
        return cur.fetchall()


def load(dwh_conn, rows, load_ts):
    """Пересоздаёт raw.airports_data и вставляет строки + технические поля."""
    with dwh_conn.cursor() as cur:
        cur.execute(CREATE_RAW_TABLE)

        records = [row + (load_ts, SOURCE_SYSTEM) for row in rows]

        psycopg2.extras.execute_values(
            cur, INSERT_SQL, records, template=INSERT_TEMPLATE
        )

    dwh_conn.commit()


def main():
    load_ts = datetime.now(timezone.utc)

    source_conn = psycopg2.connect(**SOURCE_CONN)
    dwh_conn = psycopg2.connect(**DWH_CONN)
    try:
        rows = extract(source_conn)
        print(f"Прочитано из источника: {len(rows)} строк")

        load(dwh_conn, rows, load_ts)
        print(f"Загружено в raw.airports_data: {len(rows)} строк, _loaded_at={load_ts.isoformat()}")
    finally:
        source_conn.close()
        dwh_conn.close()


if __name__ == "__main__":
    main()
