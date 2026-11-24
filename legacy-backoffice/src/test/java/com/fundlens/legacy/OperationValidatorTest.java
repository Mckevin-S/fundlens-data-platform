package com.fundlens.legacy;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.math.BigDecimal;
import java.time.LocalDate;
import org.junit.jupiter.api.Test;

class OperationValidatorTest {

    private static Operation op(String type, String isin, String quantity, String amount) {
        Operation op = new Operation();
        op.setFundId("FL-0001");
        op.setTradeDate(LocalDate.of(2026, 11, 20));
        op.setType(type);
        op.setIsin(isin);
        op.setQuantity(quantity == null ? null : new BigDecimal(quantity));
        op.setAmount(amount == null ? null : new BigDecimal(amount));
        return op;
    }

    @Test
    void achat_complet_valide() {
        assertTrue(OperationValidator.validate(op("BUY", "FR0000120271", "100", "6142.00")).isEmpty());
    }

    @Test
    void souscription_sans_titre_valide() {
        assertTrue(OperationValidator.validate(op("SUBSCRIPTION", null, null, "10000")).isEmpty());
    }

    @Test
    void vente_sans_isin_ni_quantite() {
        assertEquals(2, OperationValidator.validate(op("SELL", null, "0", "10")).size());
    }

    @Test
    void type_inconnu_et_montant_negatif() {
        assertEquals(2, OperationValidator.validate(op("SWAP", null, null, "-1")).size());
    }
}
