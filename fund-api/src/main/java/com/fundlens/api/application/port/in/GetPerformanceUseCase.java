package com.fundlens.api.application.port.in;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Performance;
import java.time.LocalDate;

public interface GetPerformanceUseCase {

    Performance performance(FundId fundId, LocalDate from, LocalDate to);
}
