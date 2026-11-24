{% test dbt_utils_free_unique_combination(model, columns) %}
-- Unicité d'une combinaison de colonnes, sans dépendre du paquet dbt_utils
select {{ columns | join(', ') }}, count(*) as occurrences
from {{ model }}
group by {{ columns | join(', ') }}
having count(*) > 1
{% endtest %}
