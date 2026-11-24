package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.time.LocalDate;

/** Alerte levée quand la VL varie plus que le seuil autorisé d'un jour à l'autre. */
public record NavAlert(FundId fundId, LocalDate asOf, BigDecimal variation, String message) {
}
