select
    ticket_no,
    book_ref,
    passenger_id,
    passenger_name,
    outbound,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'tickets') }}
