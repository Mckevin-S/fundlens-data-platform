package com.fundlens.api.application.port.out;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

public interface NavRepository {

    void save(Nav nav);

    Optional<Nav> findNav(FundId fundId, LocalDate asOf);

    /** Dernière VL strictement antérieure à la date donnée. */
    Optional<Nav> findPrevious(FundId fundId, LocalDate before);

    void saveAlert(NavAlert alert);

    List<NavAlert> alerts(FundId fundId);
}
