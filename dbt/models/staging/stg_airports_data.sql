select
    airport_code,
    airport_name ->> 'en' as airport_name,
    city ->> 'en'         as city,
    country ->> 'en'      as country,
    coordinates[0]         as longitude,
    coordinates[1]         as latitude,
    timezone,
    _loaded_at,
    _source_system
from 
    {{ source('raw', 'airports_data') }}
