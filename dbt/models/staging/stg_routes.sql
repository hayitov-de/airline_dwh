select
    route_no,
    validity,
    departure_airport,
    arrival_airport,
    airplane_code,
    days_of_week,
    scheduled_time,
    duration,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'routes') }}
