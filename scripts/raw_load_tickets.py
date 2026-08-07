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
    drop table if exists raw.tickets;
    
    create table raw.tickets (
        ticket_no            text           not null,
        book_ref             char(6)        not null,
        passenger_id         text           not null,
        passenger_name       text           not null,
        outbound             bool           not null,
        _loaded_at           timestamptz    not null,
        _source_system       text           not null
    );
"""
    
extract_sql = """
    select 
        ticket_no,
        book_ref,
        passenger_id,
        passenger_name,
        outbound::text as outbound
    from bookings.tickets
"""
insert_sql = """
    insert into raw.tickets (
        ticket_no, book_ref, passenger_id, passenger_name, outbound, _loaded_at, _source_system
    ) values %s
"""

insert_template = "(%s, %s, %s, %s, %s::bool, %s, %s)"

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
        print(f"Загружено в raw.tickets: {len(rows)} строк, _loaded_at={load_ts.isoformat()}")
    finally:
        source_conn.close()
        dwh_conn.close()

if __name__ == "__main__":
    main()