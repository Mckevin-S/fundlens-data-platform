package com.fundlens.api.adapter.web;

import com.fundlens.api.adapter.documents.FundDocument;
import com.fundlens.api.adapter.documents.FundDocumentRepository;
import com.fundlens.api.application.port.in.ComputeNavUseCase;
import com.fundlens.api.application.port.in.GetPerformanceUseCase;
import com.fundlens.api.application.port.in.ListAlertsUseCase;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import com.fundlens.api.domain.model.Performance;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/funds/{fundId}")
public class FundController {

    private final ComputeNavUseCase computeNav;
    private final GetPerformanceUseCase performance;
    private final ListAlertsUseCase alerts;
    private final FundDocumentRepository documents;

    public FundController(ComputeNavUseCase computeNav, GetPerformanceUseCase performance,
                          ListAlertsUseCase alerts, FundDocumentRepository documents) {
        this.computeNav = computeNav;
        this.performance = performance;
        this.alerts = alerts;
        this.documents = documents;
    }

    public record NavResponse(String fundId, LocalDate asOf, BigDecimal netAssets, BigDecimal navPerShare) {
        static NavResponse of(Nav nav) {
            return new NavResponse(nav.fundId().value(), nav.asOf(), nav.netAssets(), nav.navPerShare());
        }
    }

    public record PerformanceResponse(String fundId, LocalDate from, LocalDate to, BigDecimal periodReturn,
                                      Map<String, BigDecimal> contributions) {
        static PerformanceResponse of(Performance p) {
            Map<String, BigDecimal> contributions = new TreeMap<>();
            p.contributions().forEach((isin, c) -> contributions.put(isin.value(), c));
            return new PerformanceResponse(p.fundId().value(), p.from(), p.to(), p.periodReturn(), contributions);
        }
    }

    public record AlertResponse(LocalDate asOf, BigDecimal variation, String message) {
        static AlertResponse of(NavAlert a) {
            return new AlertResponse(a.asOf(), a.variation(), a.message());
        }
    }

    @PostMapping("/nav/{asOf}")
    public NavResponse computeNav(@PathVariable String fundId,
                                  @PathVariable @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate asOf) {
        return NavResponse.of(computeNav.computeNav(new FundId(fundId), asOf));
    }

    @GetMapping("/performance")
    public PerformanceResponse performance(@PathVariable String fundId,
                                           @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate from,
                                           @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate to) {
        return PerformanceResponse.of(performance.performance(new FundId(fundId), from, to));
    }

    @GetMapping("/alerts")
    public List<AlertResponse> alerts(@PathVariable String fundId) {
        return alerts.alerts(new FundId(fundId)).stream().map(AlertResponse::of).toList();
    }

    @GetMapping("/documents")
    public List<FundDocument> documents(@PathVariable String fundId) {
        return documents.findByFundIdOrderByPublishedOnDesc(new FundId(fundId).value());
    }
}
