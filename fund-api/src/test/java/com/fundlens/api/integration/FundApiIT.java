package com.fundlens.api.integration;

import static org.assertj.core.api.Assertions.assertThat;

import com.fundlens.api.adapter.documents.FundDocument;
import com.fundlens.api.adapter.documents.FundDocumentRepository;
import java.time.LocalDate;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

/** Bout en bout sur de vraies bases PostgreSQL et MongoDB (Testcontainers) avec les données de V2. */
@Testcontainers
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class FundApiIT {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Container
    @ServiceConnection
    static MongoDBContainer mongo = new MongoDBContainer("mongo:7");

    @Autowired
    TestRestTemplate http;
    @Autowired
    JdbcTemplate jdbc;
    @Autowired
    FundDocumentRepository documents;

    @Test
    @SuppressWarnings("rawtypes")
    void calcule_vl_et_performance_depuis_la_base_et_journalise() {
        ResponseEntity<Map> nav = http.postForEntity("/api/funds/FL-0001/nav/2026-11-20", null, Map.class);
        assertThat(nav.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(nav.getBody()).containsEntry("navPerShare", 13.8476);

        Map perf = http.getForObject("/api/funds/FL-0001/performance?from=2026-11-20&to=2026-11-23", Map.class);
        assertThat(perf.get("periodReturn")).isEqualTo(0.004015);

        Integer audits = jdbc.queryForObject("select count(*) from audit_log where action = 'NAV_COMPUTED'", Integer.class);
        assertThat(audits).isGreaterThanOrEqualTo(2);
    }

    @Test
    void date_sans_inventaire_404() {
        assertThat(http.postForEntity("/api/funds/FL-0001/nav/2019-01-02", null, String.class).getStatusCode())
                .isEqualTo(HttpStatus.NOT_FOUND);
    }

    @Test
    void documents_du_fonds_depuis_mongodb() {
        documents.save(new FundDocument(null, "FL-0001", "PROSPECTUS", "Prospectus FundLens Actions Europe", "fr",
                LocalDate.of(2026, 1, 15), List.of("ucits", "actions")));

        List<?> body = http.getForObject("/api/funds/FL-0001/documents", List.class);
        assertThat(body).hasSize(1);
    }
}
