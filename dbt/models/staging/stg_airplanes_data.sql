select
    airplane_code,
    model ->> 'en' as model, 
    "range", 
    speed,
    _loaded_at,
    _source_system
from
{{ source ('raw', 'airplanes_data')}} 