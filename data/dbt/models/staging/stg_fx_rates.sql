select
    cast(as_of as date) as as_of,
    currency,
    cast(rate_to_eur as decimal(20, 8)) as rate_to_eur
from {{ ref('fx_rates') }}
union all
select distinct
    cast(as_of as date) as as_of,
    'EUR' as currency,
    cast(1 as decimal(20, 8)) as rate_to_eur
from {{ ref('prices') }}
