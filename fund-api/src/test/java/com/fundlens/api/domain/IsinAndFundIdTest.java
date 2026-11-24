package com.fundlens.api.domain;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatIllegalArgumentException;

import com.fundlens.api.domain.model.FundId;
import com.fundlens.api.domain.model.Isin;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class IsinAndFundIdTest {

    @ParameterizedTest
    @ValueSource(strings = {"FR0000120271", "FR0000131104", "US0378331005"})
    void accepte_des_isin_reels(String value) {
        assertThat(new Isin(value).value()).isEqualTo(value);
    }

    @ParameterizedTest
    @ValueSource(strings = {"FR0000120272", "fr0000120271", "FR000012027", "XX"})
    void refuse_un_isin_mal_forme_ou_a_cle_fausse(String value) {
        assertThatIllegalArgumentException().isThrownBy(() -> new Isin(value));
    }

    @ParameterizedTest
    @ValueSource(strings = {"FL-1", "fl-0001", "FL-00012", ""})
    void refuse_un_identifiant_de_fonds_invalide(String value) {
        assertThatIllegalArgumentException().isThrownBy(() -> new FundId(value));
    }
}
