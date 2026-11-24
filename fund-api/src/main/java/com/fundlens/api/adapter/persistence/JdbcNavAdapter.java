package com.fundlens.api.adapter.persistence;

import com.fundlens.api.application.port.out.AuditLog;
import com.fundlens.api.application.port.out.NavRepository;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Nav;
import com.fundlens.api.domain.model.NavAlert;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.jdbc.core.namedparam.MapSqlParameterSource;
import org.springframework.jdbc.core.namedparam.NamedParameterJdbcTemplate;
import org.springframework.stereotype.Component;

/** VL calculées, alertes et journal d'audit dans PostgreSQL. */
@Component
public class JdbcNavAdapter implements NavRepository, AuditLog {

    private static final RowMapper<Nav> NAV = (rs, i) -> new Nav(new FundId(rs.getString("fund_id")),
            rs.getObject("as_of", LocalDate.class), rs.getBigDecimal("net_assets"), rs.getBigDecimal("nav_per_share"));

    private final NamedParameterJdbcTemplate jdbc;

    public JdbcNavAdapter(NamedParameterJdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @Override
    public void save(Nav nav) {
        jdbc.update("""
                insert into nav (fund_id, as_of, net_assets, nav_per_share) values (:fund, :asOf, :assets, :nav)
                on conflict (fund_id, as_of) do update
                set net_assets = excluded.net_assets, nav_per_share = excluded.nav_per_share, computed_at = now()
                """, new MapSqlParameterSource()
                .addValue("fund", nav.fundId().value()).addValue("asOf", nav.asOf())
                .addValue("assets", nav.netAssets()).addValue("nav", nav.navPerShare()));
    }

    @Override
    public Optional<Nav> findNav(FundId fundId, LocalDate asOf) {
        return jdbc.query("select * from nav where fund_id = :fund and as_of = :asOf",
                new MapSqlParameterSource().addValue("fund", fundId.value()).addValue("asOf", asOf), NAV)
                .stream().findFirst();
    }

    @Override
    public Optional<Nav> findPrevious(FundId fundId, LocalDate before) {
        return jdbc.query("select * from nav where fund_id = :fund and as_of < :before order by as_of desc limit 1",
                new MapSqlParameterSource().addValue("fund", fundId.value()).addValue("before", before), NAV)
                .stream().findFirst();
    }

    @Override
    public void saveAlert(NavAlert alert) {
        jdbc.update("insert into nav_alert (fund_id, as_of, variation, message) values (:fund, :asOf, :variation, :message)",
                new MapSqlParameterSource().addValue("fund", alert.fundId().value()).addValue("asOf", alert.asOf())
                        .addValue("variation", alert.variation()).addValue("message", alert.message()));
    }

    @Override
    public List<NavAlert> alerts(FundId fundId) {
        return jdbc.query("select * from nav_alert where fund_id = :fund order by as_of desc",
                new MapSqlParameterSource("fund", fundId.value()),
                (rs, i) -> new NavAlert(fundId, rs.getObject("as_of", LocalDate.class),
                        rs.getBigDecimal("variation"), rs.getString("message")));
    }

    @Override
    public void record(String action, String fundId, String detail) {
        jdbc.update("insert into audit_log (action, fund_id, detail) values (:action, :fund, :detail)",
                new MapSqlParameterSource().addValue("action", action).addValue("fund", fundId).addValue("detail", detail));
    }
}
