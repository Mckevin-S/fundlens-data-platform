package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Map;

/** Performance d'un fonds entre deux dates et contribution de chaque titre (en points de rendement). */
public record Performance(FundId fundId, LocalDate from, LocalDate to, BigDecimal periodReturn,
                          Map<Isin, BigDecimal> contributions) {
}
