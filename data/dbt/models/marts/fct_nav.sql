-- Data product « Conformité / Reporting » : valeur liquidative quotidienne de chaque fonds
with fund_day as (
    select distinct
        as_of,
        fund_id,
        shares_outstanding,
        cash
    from {{ ref('stg_positions') }}
),

invested as (
    select
        as_of,
        fund_id,
        sum(value_eur) as invested_eur
    from {{ ref('fct_position_valuation') }}
    group by as_of, fund_id
)

select
    fund_day.as_of,
    fund_day.fund_id,
    cast(invested.invested_eur + fund_day.cash as decimal(20, 2)) as net_assets,
    cast(round((invested.invested_eur + fund_day.cash) / fund_day.shares_outstanding, 4) as decimal(20, 4))
        as nav_per_share
from fund_day
inner join invested
    on fund_day.as_of = invested.as_of and fund_day.fund_id = invested.fund_id
