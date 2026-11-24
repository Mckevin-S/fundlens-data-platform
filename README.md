# fundlens-data-platform

> **Statut : en cours de réalisation.** Ce dépôt contient pour l'instant la conception et la feuille de route ; le code arrive lot par lot (voir « Avancement »).

Plateforme de données et d'applications pour une société de gestion d'actifs : chaque matin, valeur liquidative (VL), performance, risque et contrôles réglementaires des fonds, calculés à partir d'un back-office legacy, de fichiers de marché et d'un portail dépositaire sans API, avec un assistant IA sur la documentation des fonds.

## Problématique

Les gérants et la conformité attendent chaque matin des indicateurs fiables. Les données viennent d'un back-office Jakarta EE vieillissant sur Oracle, de fichiers de cours JSON et d'un portail dépositaire sans API ; les calculs sont faits à la main dans des tableurs.

## Fonctionnalités prévues

1. Robot UiPath qui récupère les relevés d'un portail dépositaire simulé (lancement PowerShell).
2. DAG Airflow de fin de journée : extraction Oracle (ELT), validation JSON Schema, dépôt HDFS, archive S3, chargement BigQuery.
3. Jobs Spark 3.5 en Scala sur YARN : valorisation, VL, performance, contributions.
4. Notebook Databricks (PySpark) : VaR historique par fonds.
5. Modèles dbt (BigQuery et Snowflake) et tests Elementary ; data products Positions, Marchés, Conformité.
6. `fund-api` : Spring Boot 3.3, Java 21, architecture hexagonale ; PostgreSQL + MongoDB.
7. `compliance-service` : .NET 8, contrôle des ratios réglementaires, pages Razor + Bootstrap + jQuery, publication IIS.
8. Cockpit Angular 18 des gérants ; portail investisseurs React 18 via un BFF NestJS.
9. Assistant RAG (FastAPI, LangChain, Ollama) avec un outil qui interroge `fund-api`.
10. `migration-assistant` : migration Jakarta EE → Spring Boot (OpenRewrite + LLM) et génération de tests relus.
11. `code-guard` : contrôle automatique du code (SQL, Java, JSON) en pre-commit et en CI.
12. Docker Compose, Kubernetes (kind + Helm), Terraform (GCP, AWS, Snowflake), Prometheus/Grafana, runbook.

## Architecture (cible)

```
legacy-backoffice (Jakarta EE, Oracle) ──ELT──┐
fichiers de marché JSON ──────────────────────┼─► Airflow ─► HDFS / S3 ─► Spark (Scala) ─► BigQuery / Snowflake (dbt)
portail dépositaire ──► robot UiPath ─────────┘                                              │
                                                                                             ▼
          cockpit Angular ◄── fund-api (Spring Boot) ◄──────────────────────────── data products
          portail React ◄── BFF NestJS ◄──┘        ▲
          compliance-service (.NET, IIS)           └── assistant RAG (FastAPI + Ollama)
```

## Stack

Java 21 · Spring Boot 3.3 · Jakarta EE 10 · Angular 18 · React 18 · NestJS 10 · TypeScript · .NET 8 · Python 3.12 · Scala 2.12 · Spark 3.5 · Hadoop 3.3 · Airflow 2.9 · dbt 1.8 · Elementary · BigQuery · Snowflake · Databricks · Oracle 23ai Free · PostgreSQL 16 · MongoDB 7 · Terraform 1.8 · Docker · Kubernetes (kind, Helm) · GitHub Actions · UiPath · PowerShell 7

## Arborescence prévue

```
legacy-backoffice/  fund-api/  compliance-service/  cockpit/  investor-portal/  portal-bff/
rag-assistant/  migration-assistant/  code-guard/
data/{airflow,spark,dbt,databricks}/  rpa/uipath/  infra/{compose,helm,terraform}/  docs/
```

## Avancement

| Lot | Contenu | Statut |
|---|---|---|
| L1 | Socle : Compose, CI, code-guard | à faire |
| L2 | Ingestion : UiPath, Airflow, HDFS, S3 | à faire |
| L3 | Calculs : Spark, Databricks, dbt, Elementary | à faire |
| L4 | fund-api + migration du legacy | à faire |
| L5 | compliance-service .NET / IIS | à faire |
| L6 | Cockpit Angular, portail React, BFF | à faire |
| L7 | Assistant RAG | à faire |
| L8 | Kubernetes, Terraform, supervision, démo | à faire |

## Méthode

TDD sur les calculs, Conventional Commits, Git Flow (`main`, `develop`, `feature/lot-N-*`), un lot livrable et démontrable à la fois. Tests unitaires, d'intégration (Testcontainers, dbt test) et E2E (Playwright) dans la CI.

## Auteur

Mckevin Kamguem Tchuenkam – M2 Architecture et Développement Logiciel, 3iL Ingénieurs.
