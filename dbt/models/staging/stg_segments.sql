select
    ticket_no,
    flight_id,
    fare_conditions,
    price,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'segments') }}
