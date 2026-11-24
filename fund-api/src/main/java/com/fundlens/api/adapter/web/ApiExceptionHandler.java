package com.fundlens.api.adapter.web;

import com.fundlens.api.application.port.out.UnknownSnapshotException;
import com.fundlens.api.domain.model.MissingPriceException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

/** Erreurs métier traduites en réponses RFC 9457 (application/problem+json). */
@RestControllerAdvice
public class ApiExceptionHandler {

    @ExceptionHandler(IllegalArgumentException.class)
    ProblemDetail badRequest(IllegalArgumentException e) {
        return problem(HttpStatus.BAD_REQUEST, "Requête invalide", e.getMessage());
    }

    @ExceptionHandler(UnknownSnapshotException.class)
    ProblemDetail notFound(UnknownSnapshotException e) {
        return problem(HttpStatus.NOT_FOUND, "Inventaire introuvable", e.getMessage());
    }

    @ExceptionHandler(MissingPriceException.class)
    ProblemDetail unprocessable(MissingPriceException e) {
        return problem(HttpStatus.UNPROCESSABLE_ENTITY, "Données de marché incomplètes", e.getMessage());
    }

    private static ProblemDetail problem(HttpStatus status, String title, String detail) {
        ProblemDetail problem = ProblemDetail.forStatusAndDetail(status, detail);
        problem.setTitle(title);
        return problem;
    }
}
