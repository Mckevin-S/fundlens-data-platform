package com.fundlens.api.domain.model;

import java.util.Objects;
import java.util.regex.Pattern;

/** Code ISIN d'un titre (ISO 6166), contrôle de format et de clé de Luhn. */
public record Isin(String value) {

    private static final Pattern FORMAT = Pattern.compile("^[A-Z]{2}[A-Z0-9]{9}\\d$");

    public Isin {
        Objects.requireNonNull(value, "isin");
        if (!FORMAT.matcher(value).matches() || !hasValidCheckDigit(value)) {
            throw new IllegalArgumentException("ISIN invalide : " + value);
        }
    }

    static boolean hasValidCheckDigit(String isin) {
        StringBuilder digits = new StringBuilder();
        for (char c : isin.toCharArray()) {
            digits.append(Character.isDigit(c) ? String.valueOf(c) : String.valueOf(c - 'A' + 10));
        }
        int sum = 0;
        boolean doubleIt = false;
        for (int i = digits.length() - 1; i >= 0; i--) {
            int d = digits.charAt(i) - '0';
            if (doubleIt) {
                d *= 2;
                if (d > 9) {
                    d -= 9;
                }
            }
            sum += d;
            doubleIt = !doubleIt;
        }
        return sum % 10 == 0;
    }

    @Override
    public String toString() {
        return value;
    }
}
