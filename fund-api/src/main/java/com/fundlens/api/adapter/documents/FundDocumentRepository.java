package com.fundlens.api.adapter.documents;

import java.util.List;
import org.springframework.data.mongodb.repository.MongoRepository;

public interface FundDocumentRepository extends MongoRepository<FundDocument, String> {

    List<FundDocument> findByFundIdOrderByPublishedOnDesc(String fundId);
}
