# ADR 0001 – Contrôle automatique du code avec code-guard

**Statut** : accepté – 24/11/2026

## Contexte

Le dépôt mélange Java, SQL (dbt), contrats JSON et bientôt C#, Scala et TypeScript. Les revues humaines ne suffisent pas à garantir des règles simples : pas de secret commité, domaine hexagonal sans dépendance au framework, SQL homogène, exemples conformes aux contrats des data products.

## Décision

Un outil maison, `code-guard` (Python), exécuté en pre-commit sur les fichiers modifiés et en CI sur tout le dépôt :

- `sql.*` : sqlfluff, dialecte BigQuery, sur `data/dbt` (les règles de mise en forme sont des avertissements) ;
- `java.naming`, `java.no-sysout`, `java.no-field-injection`, `java.domain-purity` ;
- `contracts.*` : chaque `contracts/<nom>.schema.json` est un schéma draft 2020-12 valide, déclare `$id` et `version`, et chaque exemple de `contracts/examples/<nom>/` le respecte ;
- `secrets.detected` : clés AWS, clés privées, jetons GitHub, mots de passe en clair.

Code de sortie 1 en cas d'erreur ; `--strict` rend aussi les avertissements bloquants.

## Conséquences

- Les règles sont testées (pytest, couverture minimale 90 %).
- Ajouter une règle = un module dans `code_guard/rules/` + ses tests.
- Les outils spécialisés (SonarQube, Trivy, OWASP ZAP) viendront en complément dans la CI des lots suivants.
