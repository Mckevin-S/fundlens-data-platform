package com.fundlens.api.adapter.documents;

import java.time.LocalDate;
import java.util.List;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

/** Métadonnées d'un document réglementaire (prospectus, DIC) stocké dans MongoDB. */
@Document("fund_documents")
public record FundDocument(@Id String id, String fundId, String type, String title, String language,
                           LocalDate publishedOn, List<String> tags) {
}
