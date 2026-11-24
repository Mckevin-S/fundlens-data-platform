package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.util.Objects;

/** Cours de clôture d'un titre dans sa devise de cotation. */
public record Price(Isin isin, String currency, BigDecimal close) {

    public Price {
        Objects.requireNonNull(isin, "isin");
        Objects.requireNonNull(currency, "currency");
        Objects.requireNonNull(close, "close");
        if (close.signum() <= 0) {
            throw new IllegalArgumentException("Le cours doit être strictement positif : " + isin);
        }
    }
}
