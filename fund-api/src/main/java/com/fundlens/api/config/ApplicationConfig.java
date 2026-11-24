package com.fundlens.api.config;

import com.fundlens.api.adapter.persistence.JdbcNavAdapter;
import com.fundlens.api.adapter.persistence.JdbcPortfolioAdapter;
import com.fundlens.api.application.service.NavService;
import com.fundlens.api.domain.service.NavAlertPolicy;
import java.math.BigDecimal;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/** Assemblage : le domaine et les cas d'usage sont instanciés ici, sans annotation Spring dans leur code. */
@Configuration
public class ApplicationConfig {

    @Bean
    NavService navService(JdbcPortfolioAdapter portfolio, JdbcNavAdapter navs,
                          @Value("${fundlens.nav.alert-threshold:0.05}") BigDecimal threshold) {
        return new NavService(portfolio, portfolio, navs, navs, new NavAlertPolicy(threshold));
    }

    @Bean
    WebMvcConfigurer cors(@Value("${fundlens.cors.allowed-origins:http://localhost:4200}") String[] origins) {
        return new WebMvcConfigurer() {
            @Override
            public void addCorsMappings(CorsRegistry registry) {
                registry.addMapping("/api/**").allowedOrigins(origins).allowedMethods("GET", "POST");
            }
        };
    }
}
