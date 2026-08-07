select
    ticket_no,
    flight_id,
    seat_no,
    boarding_no,
    boarding_time,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'boarding_passes') }}
