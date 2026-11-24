package com.fundlens.api.application.service;

import com.fundlens.api.application.port.in.ComputeNavUseCase;
import com.fundlens.api.application.port.in.GetPerformanceUseCase;
import com.fundlens.api.application.port.in.ListAlertsUseCase;
import com.fundlens.api.application.port.out.AuditLog;
import com.fundlens.api.application.port.out.MarketDataRepository;
import com.fundlens.api.application.port.out.NavRepository;
import com.fundlens.api.application.port.out.SnapshotRepository;
import com.fundlens.api.application.port.out.UnknownSnapshotException;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import com.fundlens.api.domain.model.Performance;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import com.fundlens.api.domain.model.Position;
import com.fundlens.api.domain.model.Price;
import com.fundlens.api.domain.service.NavAlertPolicy;
import com.fundlens.api.domain.service.NavCalculator;
import com.fundlens.api.domain.service.PerformanceCalculator;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/** Cas d'usage : calcul de VL, performance et alertes. Aucune dépendance au framework. */
public class NavService implements ComputeNavUseCase, GetPerformanceUseCase, ListAlertsUseCase {

    private final SnapshotRepository snapshots;
    private final MarketDataRepository marketData;
    private final NavRepository navs;
    private final AuditLog audit;
    private final NavCalculator navCalculator = new NavCalculator();
    private final PerformanceCalculator performanceCalculator = new PerformanceCalculator();
    private final NavAlertPolicy alertPolicy;

    public NavService(SnapshotRepository snapshots, MarketDataRepository marketData, NavRepository navs,
                      AuditLog audit, NavAlertPolicy alertPolicy) {
        this.snapshots = snapshots;
        this.marketData = marketData;
        this.navs = navs;
        this.audit = audit;
        this.alertPolicy = alertPolicy;
    }

    @Override
    public Nav computeNav(FundId fundId, LocalDate asOf) {
        PortfolioSnapshot snapshot = snapshot(fundId, asOf);
        Nav nav = navCalculator.compute(snapshot, prices(snapshot), marketData.fxRates(asOf));
        navs.save(nav);
        navs.findPrevious(fundId, asOf).flatMap(previous -> alertPolicy.evaluate(previous, nav)).ifPresent(alert -> {
            navs.saveAlert(alert);
            audit.record("NAV_ALERT", fundId.value(), alert.message());
        });
        audit.record("NAV_COMPUTED", fundId.value(), asOf + " VL=" + nav.navPerShare());
        return nav;
    }

    @Override
    public Performance performance(FundId fundId, LocalDate from, LocalDate to) {
        Nav start = navs.findNav(fundId, from).orElseGet(() -> computeNav(fundId, from));
        Nav end = navs.findNav(fundId, to).orElseGet(() -> computeNav(fundId, to));
        return performanceCalculator.compute(start, end, values(fundId, from), values(fundId, to));
    }

    @Override
    public List<NavAlert> alerts(FundId fundId) {
        return navs.alerts(fundId);
    }

    private Map<Isin, BigDecimal> values(FundId fundId, LocalDate asOf) {
        PortfolioSnapshot snapshot = snapshot(fundId, asOf);
        FxRates fx = marketData.fxRates(asOf);
        return navCalculator.valuePositions(snapshot, prices(snapshot), fx);
    }

    private PortfolioSnapshot snapshot(FundId fundId, LocalDate asOf) {
        return snapshots.find(fundId, asOf).orElseThrow(() ->
                new UnknownSnapshotException("Aucun inventaire pour " + fundId + " au " + asOf));
    }

    private Map<Isin, Price> prices(PortfolioSnapshot snapshot) {
        List<Isin> isins = snapshot.positions().stream().map(Position::isin).toList();
        return marketData.prices(isins, snapshot.asOf());
    }
}
