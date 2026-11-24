# Usage de l'IA dans le projet

| Où | Comment | Garde-fou |
|---|---|---|
| Développement | assistants de code (Claude, Copilot) pour proposer du code et des tests | chaque proposition est relue ; les tests sont exécutés avant commit |
| `migration-assistant` | LLM local (Ollama) pour le reste à faire de la migration et la génération de tests | sorties marquées « GÉNÉRÉ PAR IA – À RELIRE », jamais commitées sans relecture |
| `rag-assistant` | réponses limitées aux extraits des documents, sources citées ; questions chiffrées routées vers fund-api | si aucun extrait n'est pertinent, l'assistant le dit au lieu d'inventer |

Aucune clé d'API n'est nécessaire : les modèles tournent localement (Ollama).
