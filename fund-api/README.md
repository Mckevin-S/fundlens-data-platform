# fund-api

API Spring Boot 3.3 (Java 21) en architecture hexagonale : calcul de la valeur liquidative, performance et contributions, alertes de variation, documents des fonds.

| Méthode | Chemin | Rôle |
|---|---|---|
| POST | `/api/funds/{fundId}/nav/{date}` | calcule et enregistre la VL (alerte si variation > 5 %) |
| GET | `/api/funds/{fundId}/performance?from=&to=` | performance et contribution de chaque titre |
| GET | `/api/funds/{fundId}/alerts` | alertes de VL |
| GET | `/api/funds/{fundId}/documents` | documents réglementaires (MongoDB) |

Structure : `domain` (modèle et calculs, Java pur) → `application` (cas d'usage et ports) → `adapter` (JDBC PostgreSQL, MongoDB, REST) ; l'assemblage est dans `config`. ArchUnit vérifie ces dépendances.

```bash
mvn verify          # tests unitaires + tests d'intégration Testcontainers (Docker requis)
```

> **À vérifier** : ce module a été écrit sans pouvoir être compilé dans l'environnement de développement (Maven Central inaccessible). Le domaine et l'application compilent avec `javac` et les valeurs attendues des tests ont été recalculées ; la compilation complète et les tests doivent être lancés avec `mvn verify`.
