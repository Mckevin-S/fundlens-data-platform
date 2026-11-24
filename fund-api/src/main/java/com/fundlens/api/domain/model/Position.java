package com.fundlens.api.domain.model;

import java.math.BigDecimal;
import java.util.Objects;

/** Quantité d'un titre détenue par un fonds. */
public record Position(Isin isin, BigDecimal quantity) {

    public Position {
        Objects.requireNonNull(isin, "isin");
        Objects.requireNonNull(quantity, "quantity");
    }
}
