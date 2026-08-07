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

create_raw_table = """
    drop table if exists raw.boarding_passes;
    
    create table raw.boarding_passes (
        ticket_no       text         not null,
        flight_id       int          not null,
        seat_no         text         not null,
        boarding_no     int,
        boarding_time   timestamptz,
        _loaded_at      timestamptz  not null,
        _source_system  text         not null
    );
"""

extract_sql = """
    select 
        ticket_no,
        flight_id::text as flight_id,
        seat_no,
        boarding_no::text as boarding_no,
        boarding_time::text as boarding_time
    from bookings.boarding_passes
"""
insert_sql = """
    insert into raw.boarding_passes (
        ticket_no, flight_id, seat_no, boarding_no, boarding_time, _loaded_at, _source_system
    ) values %s
"""

insert_template = "(%s, %s::int, %s, %s::int, %s::timestamptz, %s, %s)"

def extract(source_conn):
    with source_conn.cursor() as cur:
        cur.execute(extract_sql)
        return cur.fetchall()

def load(dwh_conn, rows, load_ts):
    with dwh_conn.cursor() as cur:
        cur.execute(create_raw_table)
        records = [row + (load_ts, SOURCE_SYSTEM) for row in rows]

        psycopg2.extras.execute_values(
            cur, insert_sql, records, template=insert_template
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
        print(f"Загружено в raw.boarding_passes: {len(rows)} строк, _loaded_at={load_ts.isoformat()}")
    finally:
        source_conn.close()
        dwh_conn.close()

if __name__ == "__main__":
    main()