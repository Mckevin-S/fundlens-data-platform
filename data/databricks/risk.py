"""Calculs de risque purs (sans Spark), utilisés par le notebook Databricks et testés en local."""

from __future__ import annotations

import math


def returns_from_navs(navs: list[float]) -> list[float]:
    return [navs[i] / navs[i - 1] - 1 for i in range(1, len(navs))]


def historical_var(returns: list[float], confidence: float) -> float:
    """Perte (positive) non dépassée avec la probabilité `confidence`, méthode historique (quantile empirique)."""
    if not returns:
        raise ValueError("au moins un rendement est nécessaire")
    if not 0 < confidence < 1:
        raise ValueError("le niveau de confiance doit être entre 0 et 1")
    ordered = sorted(returns)
    # arrondi pour neutraliser les erreurs binaires : (1 - 0,95) × 100 = 5,000000000000004
    index = max(0, math.ceil(round((1 - confidence) * len(ordered), 9)) - 1)
    return round(max(0.0, -ordered[index]), 6)
