package com.fundlens.legacy;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.time.LocalDate;

/** Opération sur titre saisie au back-office (achat, vente, souscription, rachat). */
@Entity
@Table(name = "OPERATIONS")
public class Operation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "FUND_ID", nullable = false, length = 7)
    private String fundId;

    @Column(name = "TRADE_DATE", nullable = false)
    private LocalDate tradeDate;

    @Column(name = "OP_TYPE", nullable = false, length = 12)
    private String type;

    @Column(name = "ISIN", length = 12)
    private String isin;

    @Column(name = "QUANTITY", precision = 20, scale = 4)
    private BigDecimal quantity;

    @Column(name = "AMOUNT", precision = 20, scale = 2, nullable = false)
    private BigDecimal amount;

    public Long getId() { return id; }
    public String getFundId() { return fundId; }
    public void setFundId(String fundId) { this.fundId = fundId; }
    public LocalDate getTradeDate() { return tradeDate; }
    public void setTradeDate(LocalDate tradeDate) { this.tradeDate = tradeDate; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getIsin() { return isin; }
    public void setIsin(String isin) { this.isin = isin; }
    public BigDecimal getQuantity() { return quantity; }
    public void setQuantity(BigDecimal quantity) { this.quantity = quantity; }
    public BigDecimal getAmount() { return amount; }
    public void setAmount(BigDecimal amount) { this.amount = amount; }
}
