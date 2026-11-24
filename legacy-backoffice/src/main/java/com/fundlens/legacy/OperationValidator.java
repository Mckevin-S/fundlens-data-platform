package com.fundlens.legacy;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** Règles de saisie historiques, reprises à l'identique par la migration. */
public final class OperationValidator {

    static final Set<String> SECURITY_TYPES = Set.of("BUY", "SELL");
    static final Set<String> CAPITAL_TYPES = Set.of("SUBSCRIPTION", "REDEMPTION");

    private OperationValidator() {
    }

    public static List<String> validate(Operation op) {
        List<String> errors = new ArrayList<>();
        if (op.getFundId() == null || !op.getFundId().matches("FL-\\d{4}")) {
            errors.add("fundId invalide");
        }
        if (op.getTradeDate() == null) {
            errors.add("tradeDate obligatoire");
        }
        if (op.getAmount() == null || op.getAmount().signum() <= 0) {
            errors.add("amount doit être positif");
        }
        String type = op.getType();
        if (SECURITY_TYPES.contains(type)) {
            if (op.getIsin() == null || op.getIsin().length() != 12) {
                errors.add("isin obligatoire pour " + type);
            }
            if (op.getQuantity() == null || op.getQuantity().compareTo(BigDecimal.ZERO) <= 0) {
                errors.add("quantity doit être positive pour " + type);
            }
        } else if (!CAPITAL_TYPES.contains(type)) {
            errors.add("type inconnu : " + type);
        }
        return errors;
    }
}
