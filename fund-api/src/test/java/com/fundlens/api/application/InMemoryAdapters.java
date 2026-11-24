package com.fundlens.api.application;

import com.fundlens.api.application.port.out.AuditLog;
import com.fundlens.api.application.port.out.MarketDataRepository;
import com.fundlens.api.application.port.out.NavRepository;
import com.fundlens.api.application.port.out.SnapshotRepository;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import com.fundlens.api.domain.model.Price;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

/** Adaptateurs en mémoire pour tester les cas d'usage sans base de données. */
final class InMemoryAdapters implements SnapshotRepository, MarketDataRepository, NavRepository, AuditLog {

    final Map<String, PortfolioSnapshot> snapshots = new HashMap<>();
    final Map<LocalDate, Map<Isin, Price>> prices = new HashMap<>();
    final Map<String, Nav> navs = new HashMap<>();
    final List<NavAlert> alerts = new ArrayList<>();
    final List<String> audit = new ArrayList<>();
    FxRates fx = FxRates.eurOnly();

    private static String key(FundId id, LocalDate d) {
        return id + "@" + d;
    }

    @Override
    public Optional<PortfolioSnapshot> find(FundId fundId, LocalDate asOf) {
        return Optional.ofNullable(snapshots.get(key(fundId, asOf)));
    }

    @Override
    public Map<Isin, Price> prices(Collection<Isin> isins, LocalDate asOf) {
        return prices.getOrDefault(asOf, Map.of()).entrySet().stream()
                .filter(e -> isins.contains(e.getKey()))
                .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
    }

    @Override
    public FxRates fxRates(LocalDate asOf) {
        return fx;
    }

    @Override
    public void save(Nav nav) {
        navs.put(key(nav.fundId(), nav.asOf()), nav);
    }

    @Override
    public Optional<Nav> findNav(FundId fundId, LocalDate asOf) {
        return Optional.ofNullable(navs.get(key(fundId, asOf)));
    }

    @Override
    public Optional<Nav> findPrevious(FundId fundId, LocalDate before) {
        return navs.values().stream()
                .filter(n -> n.fundId().equals(fundId) && n.asOf().isBefore(before))
                .max(Comparator.comparing(Nav::asOf));
    }

    @Override
    public void saveAlert(NavAlert alert) {
        alerts.add(alert);
    }

    @Override
    public List<NavAlert> alerts(FundId fundId) {
        return alerts.stream().filter(a -> a.fundId().equals(fundId)).toList();
    }

    @Override
    public void record(String action, String fundId, String detail) {
        audit.add(action + " " + fundId);
    }
}
