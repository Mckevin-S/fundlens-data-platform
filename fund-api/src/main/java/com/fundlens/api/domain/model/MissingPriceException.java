package com.fundlens.api.domain.model;

/** Un titre en portefeuille n'a pas de cours (ou pas de taux de change) à la date demandée. */
public class MissingPriceException extends RuntimeException {

    public MissingPriceException(String message) {
        super(message);
    }
}
