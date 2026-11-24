package com.fundlens.api.application.port.in;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.NavAlert;
import java.util.List;

public interface ListAlertsUseCase {

    List<NavAlert> alerts(FundId fundId);
}
