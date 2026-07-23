import pytest
from core.bic_table import BIC_COMPANY_MAP
from containers.service import validate_bic_company


class TestBicTable:
    def test_table_not_empty(self):
        assert len(BIC_COMPANY_MAP) > 0

    def test_known_codes_present(self):
        for code in ["MSCU", "MAEU", "HLXU", "CMAU", "TRKU", "ARKU"]:
            assert code in BIC_COMPANY_MAP, f"{code} BIC tablosunda bulunamadı"

    def test_all_keys_are_4_uppercase_letters(self):
        for code in BIC_COMPANY_MAP:
            assert len(code) == 4 and code.isupper(), f"Geçersiz BIC kodu: {code}"

    def test_all_values_are_nonempty_strings(self):
        for code, name in BIC_COMPANY_MAP.items():
            assert isinstance(name, str) and name.strip(), f"{code} için şirket adı boş"


class TestBicValidation:
    def test_known_bic_correct_company(self):
        assert validate_bic_company("MSCU1234567", "MEDITERRANEAN SHIPPING COMPANY (MSC)") is True

    def test_known_bic_wrong_company(self):
        assert validate_bic_company("MSCU1234567", "MAERSK LINE") is False

    def test_unknown_bic_passes(self):
        # Bilinmeyen BIC kodu — geçirmeli
        assert validate_bic_company("XXXX1234567", "HERHANGI BİR ŞİRKET") is True

    def test_partial_match_accepted(self):
        # Backend partial match yapıyor: expected in company veya company in expected
        assert validate_bic_company("TRKU1234567", "TURKON LINE") is True

    def test_case_insensitive(self):
        assert validate_bic_company("MAEU9876543", "maersk line") is True
