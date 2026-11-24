package com.fundlens.api.adapter.persistence;

import com.fundlens.api.application.port.out.MarketDataRepository;
import com.fundlens.api.application.port.out.SnapshotRepository;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.FxRates;
import com.fundlens.api.domain.model.Isin;
import com.fundlens.api.domain.model.PortfolioSnapshot;
import com.fundlens.api.domain.model.Position;
import com.fundlens.api.domain.model.Price;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Component;

/** Inventaires, cours et taux de change lus dans PostgreSQL (alimenté par le pipeline de données). */
@Component
public class JdbcPortfolioAdapter implements SnapshotRepository, MarketDataRepository {

    private final NamedParameterJdbcTemplate jdbc;

    public JdbcPortfolioAdapter(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public Optional<PortfolioSnapshot> find(FundId fundId, LocalDate asOf) {
        var params = new MapSqlParameterSource().addValue("fund", fundId.value()).addValue("asOf", asOf);
        List<Map<String, Object>> rows = jdbc.queryForList(
                "select id, shares_outstanding, cash from snapshot where fund_id = :fund and as_of = :asOf", params);
        if (rows.isEmpty()) {
            return Optional.empty();
        }
        Map<String, Object> row = rows.getFirst();
        List<Position> positions = jdbc.query(
                "select isin, quantity from snapshot_position where snapshot_id = :id order by isin",
                new MapSqlParameterSource("id", row.get("id")),
                (rs, i) -> new Position(new Isin(rs.getString("isin")), rs.getBigDecimal("quantity")));
        return Optional.of(new PortfolioSnapshot(fundId, asOf, (BigDecimal) row.get("shares_outstanding"),
                (BigDecimal) row.get("cash"), positions));
    }

    @Override
    public Map<Isin, Price> prices(Collection<Isin> isins, LocalDate asOf) {
        if (isins.isEmpty()) {
            return Map.of();
        }
        var params = new MapSqlParameterSource()
                .addValue("isins", isins.stream().map(Isin::value).toList())
                .addValue("asOf", asOf);
        Map<Isin, Price> prices = new HashMap<>();
        jdbc.query("select isin, currency, close from price where as_of = :asOf and isin in (:isins)", params, rs -> {
            Isin isin = new Isin(rs.getString("isin"));
            prices.put(isin, new Price(isin, rs.getString("currency"), rs.getBigDecimal("close")));
        });
        return prices;
    }

    @Override
    public FxRates fxRates(LocalDate asOf) {
        Map<String, BigDecimal> rates = new HashMap<>();
        jdbc.query("select currency, rate_to_eur from fx_rate where as_of = :asOf",
                new MapSqlParameterSource("asOf", asOf),
                rs -> {
                    rates.put(rs.getString("currency"), rs.getBigDecimal("rate_to_eur"));
                });
        return new FxRates(rates);
    }
}
