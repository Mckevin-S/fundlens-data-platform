package com.fundlens.api.application.port.out;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import java.time.LocalDate;
import java.util.Optional;

public interface SnapshotRepository {

    Optional<PortfolioSnapshot> find(FundId fundId, LocalDate asOf);
}
