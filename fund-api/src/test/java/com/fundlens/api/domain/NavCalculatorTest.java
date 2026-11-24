package com.fundlens.api.domain;

import static com.fundlens.api.domain.Fixtures.AAPL;
import static com.fundlens.api.domain.Fixtures.D1;
import static com.fundlens.api.domain.Fixtures.FX;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.MissingPriceException;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.Price;
import com.fundlens.api.domain.service.NavCalculator;
import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.Test;

class NavCalculatorTest {

    private final NavCalculator calculator = new NavCalculator();

    @Test
    void calcule_l_actif_net_et_la_vl_en_convertissant_les_devises() {
        // 12000 × 61,42 + 8500 × 74,18 + 1500 × 228,35 × 0,92 + 48 250,75 = 1 730 943,75 €
        Nav nav = calculator.compute(Fixtures.snapshot(D1), Fixtures.pricesD1(), FX);

        assertThat(nav.netAssets()).isEqualByComparingTo("1730943.75");
        assertThat(nav.navPerShare()).isEqualByComparingTo("13.8476");
        assertThat(nav.navPerShare().scale()).isEqualTo(NavCalculator.NAV_SCALE);
    }

    @Test
    void valorise_chaque_ligne_en_euros() {
        Map<Isin, BigDecimal> values = calculator.valuePositions(Fixtures.snapshot(D1), Fixtures.pricesD1(), FX);

        assertThat(values.get(AAPL)).isEqualByComparingTo("315123.00");
    }

    @Test
    void refuse_un_titre_sans_cours() {
        Map<Isin, Price> prices = new HashMap<>(Fixtures.pricesD1());
        prices.remove(AAPL);

        assertThatThrownBy(() -> calculator.compute(Fixtures.snapshot(D1), prices, FX))
                .isInstanceOf(MissingPriceException.class)
                .hasMessageContaining("US0378331005");
    }

    @Test
    void refuse_une_devise_sans_taux_de_change() {
        assertThatThrownBy(() -> calculator.compute(Fixtures.snapshot(D1), Fixtures.pricesD1(), FxRates.eurOnly()))
                .isInstanceOf(MissingPriceException.class)
                .hasMessageContaining("USD/EUR");
    }
}
