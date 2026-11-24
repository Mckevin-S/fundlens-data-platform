package com.fundlens.legacy;

import jakarta.ejb.Stateless;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import java.time.LocalDate;
import java.util.List;

@Stateless
public class OperationService {

    @PersistenceContext(unitName = "backoffice")
    private EntityManager em;

    public List<Operation> findByFundAndDate(String fundId, LocalDate date) {
        return em.createQuery("select o from Operation o where o.fundId = :fund and o.tradeDate = :date order by o.id",
                        Operation.class)
                .setParameter("fund", fundId)
                .setParameter("date", date)
                .getResultList();
    }

    public Operation create(Operation operation) {
        List<String> errors = OperationValidator.validate(operation);
        if (!errors.isEmpty()) {
            throw new IllegalArgumentException(String.join(", ", errors));
        }
        em.persist(operation);
        return operation;
    }
}
