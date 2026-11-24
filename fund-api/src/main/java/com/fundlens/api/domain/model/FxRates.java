package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/** Taux de change vers l'euro : 1 unité de devise = rate EUR. */
public final class FxRates {

    public static final String BASE = "EUR";
    private final Map<String, BigDecimal> toEur;

    public FxRates(Map<String, BigDecimal> toEur) {
        this.toEur = new HashMap<>(toEur);
        this.toEur.put(BASE, BigDecimal.ONE);
    }

    public static FxRates eurOnly() {
        return new FxRates(Map.of());
    }

    public Optional<BigDecimal> toEur(String currency) {
        return Optional.ofNullable(toEur.get(currency));
    }
}
