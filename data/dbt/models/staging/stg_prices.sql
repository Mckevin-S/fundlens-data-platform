select
    cast(as_of as date) as as_of,
    isin,
    currency,
    cast(close as decimal(20, 6)) as close_price
from {{ ref('prices') }}
