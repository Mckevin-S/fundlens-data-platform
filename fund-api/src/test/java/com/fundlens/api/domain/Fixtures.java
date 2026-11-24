package com.fundlens.api.domain;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import com.fundlens.api.domain.model.Position;
import com.fundlens.api.domain.model.Price;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/** Jeu de données partagé : fonds FL-0001, trois titres dont un en USD. */
public final class Fixtures {

    public static final FundId FUND = new FundId("FL-0001");
    public static final Isin TTE = new Isin("FR0000120271");
    public static final Isin BNP = new Isin("FR0000131104");
    public static final Isin AAPL = new Isin("US0378331005");
    public static final LocalDate D1 = LocalDate.of(2026, 11, 20);
    public static final LocalDate D2 = LocalDate.of(2026, 11, 23);
    public static final FxRates FX = new FxRates(Map.of("USD", new BigDecimal("0.92")));

    private Fixtures() {
    }

    public static PortfolioSnapshot snapshot(LocalDate asOf) {
        return new PortfolioSnapshot(FUND, asOf, new BigDecimal("125000"), new BigDecimal("48250.75"), List.of(
                new Position(TTE, new BigDecimal("12000")),
                new Position(BNP, new BigDecimal("8500")),
                new Position(AAPL, new BigDecimal("1500"))));
    }

    public static Map<Isin, Price> pricesD1() {
        return Map.of(TTE, price(TTE, "EUR", "61.42"), BNP, price(BNP, "EUR", "74.18"), AAPL, price(AAPL, "USD", "228.35"));
    }

    public static Map<Isin, Price> pricesD2() {
        return Map.of(TTE, price(TTE, "EUR", "63.00"), BNP, price(BNP, "EUR", "72.50"), AAPL, price(AAPL, "USD", "230.00"));
    }

    public static Price price(Isin isin, String currency, String close) {
        return new Price(isin, currency, new BigDecimal(close));
    }
}
