package com.fundlens.api.application.port.out;

/** Journal d'audit : qui a déclenché quel calcul, sur quel fonds, avec quel résultat. */
public interface AuditLog {

    void record(String action, String fundId, String detail);
}
