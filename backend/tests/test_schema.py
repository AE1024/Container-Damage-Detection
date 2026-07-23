import pytest
from pydantic import ValidationError
from containers.schema import ContainerData
from auth.schema import RegisterRequest, LoginRequest


class TestContainerSchema:
    def test_valid_container(self):
        c = ContainerData(
            container_no="MSCU1234567",
            container_type="Kuru Yük",
            company_name="MSC",
            arrive_port="Ambarlı Terminali",
            destination_port="Rotterdam Terminali",
        )
        assert c.container_no == "MSCU1234567"

    def test_container_no_lowercase_normalized(self):
        c = ContainerData(
            container_no="mscu1234567",
            container_type="Tank",
            company_name="MSC",
            arrive_port="A",
            destination_port="B",
        )
        assert c.container_no == "MSCU1234567"

    def test_invalid_container_no_short(self):
        with pytest.raises(ValidationError):
            ContainerData(
                container_no="MSCU123",
                container_type="Kuru Yük",
                company_name="MSC",
                arrive_port="A",
                destination_port="B",
            )

    def test_invalid_container_type(self):
        with pytest.raises(ValidationError):
            ContainerData(
                container_no="MSCU1234567",
                container_type="Geçersiz Tip",
                company_name="MSC",
                arrive_port="A",
                destination_port="B",
            )

    def test_company_name_uppercased(self):
        c = ContainerData(
            container_no="MSCU1234567",
            container_type="Soğutmalı",
            company_name="maersk line",
            arrive_port="A",
            destination_port="B",
        )
        assert c.company_name == "MAERSK LINE"

    def test_all_valid_container_types(self):
        valid_types = ["Kuru Yük", "Soğutmalı", "Açık Üst", "Platform", "Tank", "Özel Amaçlı"]
        for t in valid_types:
            c = ContainerData(
                container_no="MSCU1234567",
                container_type=t,
                company_name="MSC",
                arrive_port="A",
                destination_port="B",
            )
            assert c.container_type == t


class TestAuthSchema:
    def test_valid_register(self):
        r = RegisterRequest(
            first_name="Anıl",
            last_name="Elmaz",
            username="anil_test",
            company="CoreX",
            password="sifre123",
        )
        assert r.username == "anil_test"

    def test_username_too_short(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="A", last_name="B",
                username="ab", company="C", password="123456",
            )

    def test_username_invalid_chars(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="A", last_name="B",
                username="anil elmaz", company="C", password="123456",
            )

    def test_password_too_short(self):
        with pytest.raises(ValidationError):
            RegisterRequest(
                first_name="A", last_name="B",
                username="anil_test", company="C", password="123",
            )

    def test_login_only_username_password_required(self):
        # Ad/soyad artık opsiyonel
        req = LoginRequest(username="anil_test", password="sifre123")
        assert req.first_name is None
        assert req.last_name is None

    def test_login_with_optional_names(self):
        req = LoginRequest(
            username="anil_test",
            password="sifre123",
            first_name="Anıl",
            last_name="Elmaz",
        )
        assert req.first_name == "Anıl"
