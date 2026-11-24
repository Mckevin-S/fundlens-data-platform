package com.fundlens.api.domain.service;

import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.MissingPriceException;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import com.fundlens.api.domain.model.Position;
import com.fundlens.api.domain.model.Price;
import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Valorisation d'un portefeuille et calcul de la valeur liquidative.
 * VL = (somme des quantités × cours × taux de change + liquidités) / parts en circulation.
 */
public final class NavCalculator {

    public static final int NAV_SCALE = 4;
    static final int AMOUNT_SCALE = 2;

    public Nav compute(PortfolioSnapshot snapshot, Map<Isin, Price> prices, FxRates fx) {
        BigDecimal netAssets = valuePositions(snapshot, prices, fx).values().stream()
                .reduce(snapshot.cash(), BigDecimal::add)
                .setScale(AMOUNT_SCALE, RoundingMode.HALF_EVEN);
        BigDecimal navPerShare = netAssets.divide(snapshot.sharesOutstanding(), NAV_SCALE, RoundingMode.HALF_EVEN);
        return new Nav(snapshot.fundId(), snapshot.asOf(), netAssets, navPerShare);
    }

    /** Valeur en EUR de chaque ligne du portefeuille. */
    public Map<Isin, BigDecimal> valuePositions(PortfolioSnapshot snapshot, Map<Isin, Price> prices, FxRates fx) {
        Map<Isin, BigDecimal> values = new LinkedHashMap<>();
        for (Position position : snapshot.positions()) {
            Price price = prices.get(position.isin());
            if (price == null) {
                throw new MissingPriceException("Pas de cours pour " + position.isin() + " au " + snapshot.asOf());
            }
            BigDecimal rate = fx.toEur(price.currency()).orElseThrow(() ->
                    new MissingPriceException("Pas de taux de change " + price.currency() + "/EUR au " + snapshot.asOf()));
            values.merge(position.isin(), position.quantity().multiply(price.close()).multiply(rate), BigDecimal::add);
        }
        return values;
    }
}
