package com.fundlens.api.application.port.in;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Nav;
import java.time.LocalDate;

public interface ComputeNavUseCase {

    /** Calcule, enregistre et renvoie la VL du fonds à la date donnée. */
    Nav computeNav(FundId fundId, LocalDate asOf);
}
