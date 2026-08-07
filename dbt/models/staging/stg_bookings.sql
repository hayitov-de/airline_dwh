select
    book_ref,
    book_date,
    total_amount,
    _loaded_at,
    _source_system
from
    {{ source('raw', 'bookings') }}
