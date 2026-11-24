select
    cast(as_of as date) as as_of,
    fund_id,
    isin,
    cast(quantity as decimal(20, 4)) as quantity,
    cast(shares_outstanding as decimal(20, 4)) as shares_outstanding,
    cast(cash as decimal(20, 2)) as cash
from {{ ref('positions') }}
