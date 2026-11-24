package com.fundlens.api.application.port.out;

import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.Price;
import java.time.LocalDate;
import java.util.Collection;
import java.util.Map;

public interface MarketDataRepository {

    Map<Isin, Price> prices(Collection<Isin> isins, LocalDate asOf);

    FxRates fxRates(LocalDate asOf);
}
