package com.fundlens.api.domain.service;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.Performance;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Set;

/**
 * Performance entre deux VL et contribution de chaque titre :
 * contribution(titre) = (valeur fin − valeur début) / actif net début.
 */
public final class PerformanceCalculator {

    static final int RATE_SCALE = 6;

    public Performance compute(Nav start, Nav end, Map<Isin, BigDecimal> startValues, Map<Isin, BigDecimal> endValues) {
        FundId fundId = start.fundId();
        if (!fundId.equals(end.fundId())) {
            throw new IllegalArgumentException("Les deux VL doivent concerner le même fonds");
        }
        if (!end.asOf().isAfter(start.asOf())) {
            throw new IllegalArgumentException("La date de fin doit être postérieure à la date de début");
        }
        BigDecimal periodReturn = end.navPerShare()
                .divide(start.navPerShare(), MathContext.DECIMAL64)
                .subtract(BigDecimal.ONE)
                .setScale(RATE_SCALE, RoundingMode.HALF_EVEN);

        Set<Isin> isins = new HashSet<>(startValues.keySet());
        isins.addAll(endValues.keySet());
        Map<Isin, BigDecimal> contributions = new LinkedHashMap<>();
        isins.stream().sorted((a, b) -> a.value().compareTo(b.value())).forEach(isin -> {
            BigDecimal delta = endValues.getOrDefault(isin, BigDecimal.ZERO)
                    .subtract(startValues.getOrDefault(isin, BigDecimal.ZERO));
            contributions.put(isin, delta.divide(start.netAssets(), RATE_SCALE, RoundingMode.HALF_EVEN));
        });
        return new Performance(fundId, start.asOf(), end.asOf(), periodReturn, contributions);
    }
}
