package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Objects;

/** Inventaire d'un fonds en fin de journée : positions, liquidités (en EUR) et parts en circulation. */
public record PortfolioSnapshot(FundId fundId, LocalDate asOf, BigDecimal sharesOutstanding,
                                BigDecimal cash, List<Position> positions) {

    public PortfolioSnapshot {
        Objects.requireNonNull(fundId, "fundId");
        Objects.requireNonNull(asOf, "asOf");
        Objects.requireNonNull(cash, "cash");
        Objects.requireNonNull(sharesOutstanding, "sharesOutstanding");
        if (sharesOutstanding.signum() <= 0) {
            throw new IllegalArgumentException("Le nombre de parts doit être strictement positif");
        }
        positions = List.copyOf(positions);
    }
}
