select
    flight_id,
    route_no,
    status,
    scheduled_departure,
    scheduled_arrival,
    actual_departure,
    actual_arrival,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'flights') }}
