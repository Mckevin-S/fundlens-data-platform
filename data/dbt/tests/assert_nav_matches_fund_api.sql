-- Les VL calculées par dbt doivent égaler celles de fund-api pour le jeu de référence
select
    as_of,
    nav_per_share
from {{ ref('fct_nav') }}
where
    fund_id = 'FL-0001'
    and (
        (as_of = date '2026-11-20' and nav_per_share <> 13.8476)
        or (as_of = date '2026-11-23' and nav_per_share <> 13.9032)
    )
