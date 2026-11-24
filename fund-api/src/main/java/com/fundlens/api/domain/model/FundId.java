package com.fundlens.api.domain.model;

import java.util.Objects;
import java.util.regex.Pattern;

/** Identifiant d'un fonds, au format FL-0000. */
public record FundId(String value) {

    private static final Pattern FORMAT = Pattern.compile("^FL-\\d{4}$");

    public FundId {
        Objects.requireNonNull(value, "fundId");
        if (!FORMAT.matcher(value).matches()) {
            throw new IllegalArgumentException("Identifiant de fonds invalide : " + value);
        }
    }

    @Override
    public String toString() {
        return value;
    }
}
