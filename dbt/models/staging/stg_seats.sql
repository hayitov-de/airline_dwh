select
    airplane_code,
    seat_no,
    fare_conditions,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'seats') }}
