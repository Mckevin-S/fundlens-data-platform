-- Data product « Positions » : valeur en euros de chaque ligne de portefeuille
select
    positions.as_of,
    positions.fund_id,
    positions.isin,
    positions.quantity,
    prices.currency,
    prices.close_price,
    fx.rate_to_eur,
    cast(positions.quantity * prices.close_price * fx.rate_to_eur as decimal(20, 2)) as value_eur
from {{ ref('stg_positions') }} as positions
inner join {{ ref('stg_prices') }} as prices
    on positions.isin = prices.isin and positions.as_of = prices.as_of
inner join {{ ref('stg_fx_rates') }} as fx
    on prices.currency = fx.currency and prices.as_of = fx.as_of
