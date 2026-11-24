# Runbook d'exploitation

## Démarrer / arrêter

```bash
cp .env.example .env                       # renseigner les mots de passe locaux
docker compose -f infra/compose/docker-compose.yml --env-file .env up -d --build
docker compose -f infra/compose/docker-compose.yml --env-file .env --profile data up -d   # + Hadoop, Airflow, Oracle
```

| Service | URL locale |
|---|---|
| fund-api (santé, métriques) | http://localhost:8080/actuator/health · /actuator/prometheus |
| Cockpit gérants | http://localhost:4200 |
| Portail investisseurs | http://localhost:8081 |
| Conformité (.NET) | http://localhost:8085 |
| Assistant RAG | http://localhost:8000/docs |
| Portail dépositaire simulé | http://localhost:8090 |
| Airflow / HDFS / YARN | http://localhost:8089 · 9870 · 8088 |
| Prometheus / Grafana | http://localhost:9090 · http://localhost:3001 |

## Incidents courants

| Symptôme | Diagnostic | Action |
|---|---|---|
| `422 Données de marché incomplètes` sur une VL | un cours ou un taux manque pour la date | vérifier le fichier de marché du jour (contrat Marchés), relancer la tâche `validate_market_prices` |
| `404 Inventaire introuvable` | le relevé dépositaire n'a pas été chargé | relancer le robot (`rpa/run-robot.ps1 -AsOfDate …`), puis le DAG |
| Alerte « Variation de VL > 5 % » | mouvement de marché ou erreur de données | comparer avec `fct_nav` (dbt) et le job Spark ; ne pas publier avant contrôle |
| Fichier rejeté par `validate` | le fichier ne respecte pas son contrat | message d'erreur = chemin du champ fautif ; contacter le fournisseur |
| BFF en 502 | fund-api injoignable | `docker compose ps`, journaux de fund-api, santé PostgreSQL |

## Rejouer une journée

```bash
airflow dags trigger fundlens_end_of_day --exec-date 2026-11-20
dbt build --profiles-dir data/dbt --target bigquery --select fct_nav+
```
