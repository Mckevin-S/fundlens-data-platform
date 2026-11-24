package com.fundlens.api.adapter.web;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fundlens.api.adapter.documents.FundDocumentRepository;
import com.fundlens.api.application.port.in.ComputeNavUseCase;
import com.fundlens.api.application.port.in.GetPerformanceUseCase;
import com.fundlens.api.application.port.in.ListAlertsUseCase;
import com.fundlens.api.application.port.out.UnknownSnapshotException;
import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.MissingPriceException;
import com.fundlens.api.domain.model.Nav;
import java.math.BigDecimal;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(FundController.class)
class FundControllerTest {

    @Autowired
    MockMvc mvc;
    @MockBean
    ComputeNavUseCase computeNav;
    @MockBean
    GetPerformanceUseCase performance;
    @MockBean
    ListAlertsUseCase alerts;
    @MockBean
    FundDocumentRepository documents;

    @Test
    void calcule_la_vl() throws Exception {
        LocalDate d = LocalDate.of(2026, 11, 20);
        when(computeNav.computeNav(new FundId("FL-0001"), d))
                .thenReturn(new Nav(new FundId("FL-0001"), d, new BigDecimal("1730943.75"), new BigDecimal("13.8476")));

        mvc.perform(post("/api/funds/FL-0001/nav/2026-11-20"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.navPerShare").value(13.8476))
                .andExpect(jsonPath("$.fundId").value("FL-0001"));
    }

    @Test
    void identifiant_invalide_400() throws Exception {
        mvc.perform(post("/api/funds/XX/nav/2026-11-20"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.title").value("Requête invalide"));
    }

    @Test
    void inventaire_absent_404_et_cours_manquant_422() throws Exception {
        when(computeNav.computeNav(any(), any())).thenThrow(new UnknownSnapshotException("absent"));
        mvc.perform(post("/api/funds/FL-0001/nav/2020-01-01")).andExpect(status().isNotFound());

        when(computeNav.computeNav(any(), any())).thenThrow(new MissingPriceException("cours"));
        mvc.perform(post("/api/funds/FL-0001/nav/2020-01-01")).andExpect(status().isUnprocessableEntity());
    }

    @Test
    void liste_vide_d_alertes() throws Exception {
        mvc.perform(get("/api/funds/FL-0001/alerts")).andExpect(status().isOk()).andExpect(jsonPath("$").isEmpty());
    }
}
