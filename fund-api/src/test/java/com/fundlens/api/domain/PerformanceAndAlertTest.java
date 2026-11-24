package com.fundlens.api.domain;

import static com.fundlens.api.domain.Fixtures.AAPL;
import static com.fundlens.api.domain.Fixtures.BNP;
import static com.fundlens.api.domain.Fixtures.D1;
import static com.fundlens.api.domain.Fixtures.D2;
import static com.fundlens.api.domain.Fixtures.FX;
import static com.fundlens.api.domain.Fixtures.TTE;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;

import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import com.fundlens.api.domain.model.Performance;
import com.fundlens.api.domain.service.NavAlertPolicy;
import com.fundlens.api.domain.service.NavCalculator;
import com.fundlens.api.domain.service.PerformanceCalculator;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class PerformanceAndAlertTest {

    private final NavCalculator nav = new NavCalculator();
    private final Nav navD1 = nav.compute(Fixtures.snapshot(D1), Fixtures.pricesD1(), FX);
    private final Nav navD2 = nav.compute(Fixtures.snapshot(D2), Fixtures.pricesD2(), FX);

    @Test
    void calcule_la_performance_et_les_contributions_par_titre() {
        Performance perf = new PerformanceCalculator().compute(navD1, navD2,
                nav.valuePositions(Fixtures.snapshot(D1), Fixtures.pricesD1(), FX),
                nav.valuePositions(Fixtures.snapshot(D2), Fixtures.pricesD2(), FX));

        assertThat(navD2.navPerShare()).isEqualByComparingTo("13.9032");
        assertThat(perf.periodReturn()).isEqualByComparingTo("0.004015");
        assertThat(perf.contributions().get(TTE)).isEqualByComparingTo("0.010954");
        assertThat(perf.contributions().get(BNP)).isEqualByComparingTo("-0.008250");
        assertThat(perf.contributions().get(AAPL)).isEqualByComparingTo("0.001315");
    }

    @Test
    void refuse_une_periode_inversee() {
        assertThatIllegalArgumentException().isThrownBy(() ->
                new PerformanceCalculator().compute(navD2, navD1, java.util.Map.of(), java.util.Map.of()));
    }

    @Test
    void pas_d_alerte_sous_le_seuil() {
        assertThat(new NavAlertPolicy(new BigDecimal("0.05")).evaluate(navD1, navD2)).isEmpty();
    }

    @Test
    void alerte_au_dela_du_seuil() {
        Nav crash = new Nav(navD1.fundId(), LocalDate.of(2026, 11, 24), navD1.netAssets(), new BigDecimal("12.9000"));

        Optional<NavAlert> alert = new NavAlertPolicy(new BigDecimal("0.05")).evaluate(navD1, crash);

        assertThat(alert).hasValueSatisfying(a -> {
            assertThat(a.variation()).isEqualByComparingTo("-0.068431");
            assertThat(a.message()).contains("-6.84 %").contains("seuil 5 %");
        });
    }

    @Test
    void refuse_un_seuil_nul() {
        assertThatIllegalArgumentException().isThrownBy(() -> new NavAlertPolicy(BigDecimal.ZERO));
    }
}
