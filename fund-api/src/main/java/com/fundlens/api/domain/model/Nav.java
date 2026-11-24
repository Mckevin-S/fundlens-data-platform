package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.time.LocalDate;

/** Valeur liquidative calculée : actif net total (EUR) et valeur d'une part. */
public record Nav(FundId fundId, LocalDate asOf, BigDecimal netAssets, BigDecimal navPerShare) {
}
