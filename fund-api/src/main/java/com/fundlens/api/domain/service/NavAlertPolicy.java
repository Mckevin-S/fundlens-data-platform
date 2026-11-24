package com.fundlens.api.domain.service;

import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.Optional;

/** Lève une alerte quand la VL varie, en valeur absolue, plus que le seuil (ex. 0.05 = 5 %). */
public final class NavAlertPolicy {

    private final BigDecimal threshold;

    public NavAlertPolicy(BigDecimal threshold) {
        if (threshold.signum() <= 0) {
            throw new IllegalArgumentException("Le seuil doit être strictement positif");
        }
        this.threshold = threshold;
    }

    public Optional<NavAlert> evaluate(Nav previous, Nav current) {
        BigDecimal variation = current.navPerShare()
                .divide(previous.navPerShare(), MathContext.DECIMAL64)
                .subtract(BigDecimal.ONE)
                .setScale(6, RoundingMode.HALF_EVEN);
        if (variation.abs().compareTo(threshold) <= 0) {
            return Optional.empty();
        }
        String message = "Variation de VL de %s %% (seuil %s %%) : à contrôler avant publication".formatted(
                variation.movePointRight(2).setScale(2, RoundingMode.HALF_EVEN),
                threshold.movePointRight(2).stripTrailingZeros().toPlainString());
        return Optional.of(new NavAlert(current.fundId(), current.asOf(), variation, message));
    }
}
