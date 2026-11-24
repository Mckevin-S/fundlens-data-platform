package com.fundlens.api.application;

import static com.fundlens.api.domain.Fixtures.D1;
import static com.fundlens.api.domain.Fixtures.D2;
import static com.fundlens.api.domain.Fixtures.FUND;
import static com.fundlens.api.domain.Fixtures.FX;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.fundlens.api.application.port.out.UnknownSnapshotException;
import com.fundlens.api.application.service.NavService;
import com.fundlens.api.domain.Fixtures;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.Performance;
import com.fundlens.api.domain.model.Price;
import com.fundlens.api.domain.service.NavAlertPolicy;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class NavServiceTest {

    private InMemoryAdapters store;
    private NavService service;

    @BeforeEach
    void setUp() {
        store = new InMemoryAdapters();
        store.fx = FX;
        store.snapshots.put(FUND + "@" + D1, Fixtures.snapshot(D1));
        store.snapshots.put(FUND + "@" + D2, Fixtures.snapshot(D2));
        store.prices.put(D1, Fixtures.pricesD1());
        store.prices.put(D2, Fixtures.pricesD2());
        service = new NavService(store, store, store, store, new NavAlertPolicy(new BigDecimal("0.05")));
    }

    @Test
    void calcule_enregistre_et_audite_la_vl() {
        Nav nav = service.computeNav(FUND, D1);

        assertThat(nav.navPerShare()).isEqualByComparingTo("13.8476");
        assertThat(store.findNav(FUND, D1)).contains(nav);
        assertThat(store.audit).containsExactly("NAV_COMPUTED FL-0001");
    }

    @Test
    void la_performance_calcule_les_vl_manquantes() {
        Performance perf = service.performance(FUND, D1, D2);

        assertThat(perf.periodReturn()).isEqualByComparingTo("0.004015");
        assertThat(store.navs).hasSize(2);
    }

    @Test
    void leve_une_alerte_si_la_vl_chute_de_plus_de_5_pourcents() {
        LocalDate d3 = LocalDate.of(2026, 11, 24);
        store.snapshots.put(FUND + "@" + d3, Fixtures.snapshot(d3));
        Map<Isin, Price> crash = new HashMap<>();
        Fixtures.pricesD1().forEach((isin, p) ->
                crash.put(isin, new Price(isin, p.currency(), p.close().multiply(new BigDecimal("0.90")))));
        store.prices.put(d3, crash);

        service.computeNav(FUND, D1);
        service.computeNav(FUND, d3);

        assertThat(service.alerts(FUND)).singleElement()
                .satisfies(a -> assertThat(a.variation()).isNegative());
        assertThat(store.audit).contains("NAV_ALERT FL-0001");
    }

    @Test
    void inventaire_absent() {
        assertThatThrownBy(() -> service.computeNav(FUND, LocalDate.of(2020, 1, 1)))
                .isInstanceOf(UnknownSnapshotException.class);
    }
}
