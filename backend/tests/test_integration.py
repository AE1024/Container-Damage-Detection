"""
Entegrasyon testleri — gerçek FastAPI app + gerçek MongoDB Atlas.
Her test kendi yarattığı veriyi sonda temizler.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
BASE   = "/api/v1"

# ── Sabitler ────────────────────────────────────────────────────────────────
TEST_USER = {
    "first_name": "CI",
    "last_name":  "Test",
    "username":   "ci_test_runner",
    "company":    "TestCo",
    "password":   "sifre_ci_123",
}
TEST_CONTAINER = {
    "container_no":    "MSCU9990001",
    "container_type":  "Kuru Yük",
    "company_name":    "MEDITERRANEAN SHIPPING COMPANY (MSC)",
    "arrive_port":     "Ambarlı Terminali",
    "destination_port":"Rotterdam Terminali",
}


# ── Yardımcı: token al (kayıt veya login) ───────────────────────────────────
def _get_token() -> str:
    """Test kullanıcısını kayıt et, token döndür. Zaten varsa login yap."""
    res = client.post(f"{BASE}/auth/register", json=TEST_USER)
    if res.status_code == 201:
        return res.json()["access_token"]
    # Kullanıcı zaten varsa login
    res = client.post(f"{BASE}/auth/login", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"],
    })
    assert res.status_code == 200, f"Login başarısız: {res.text}"
    return res.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ── AUTH TESTLERİ ────────────────────────────────────────────────────────────
class TestAuth:

    def test_register_success(self):
        body = {**TEST_USER, "username": "ci_reg_only",
                "first_name": "Reg", "last_name": "Only"}
        res = client.post(f"{BASE}/auth/register", json=body)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert data["full_name"] == "Reg Only"

        # Cleanup
        client.delete(f"{BASE}/auth/me", headers=_auth(data["access_token"]))

    def test_register_duplicate_username(self):
        body = {**TEST_USER, "username": "ci_dup_test",
                "first_name": "Dup", "last_name": "Tester"}
        # İlk kayıt
        res1 = client.post(f"{BASE}/auth/register", json=body)
        assert res1.status_code == 201
        # İkinci kayıt aynı username — çakışmalı
        res2 = client.post(f"{BASE}/auth/register", json=body)
        assert res2.status_code == 409

        # Cleanup
        client.delete(f"{BASE}/auth/me",
                      headers=_auth(res1.json()["access_token"]))

    def test_login_success(self):
        token = _get_token()
        res = client.post(f"{BASE}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"],
        })
        assert res.status_code == 200
        assert "access_token" in res.json()

    def test_login_wrong_password(self):
        _get_token()  # kullanıcının var olduğundan emin ol
        res = client.post(f"{BASE}/auth/login", json={
            "username": TEST_USER["username"],
            "password": "yanlis_sifre",
        })
        assert res.status_code == 401

    def test_me_with_valid_token(self):
        token = _get_token()
        res = client.get(f"{BASE}/auth/me", headers=_auth(token))
        assert res.status_code == 200
        assert res.json()["full_name"] == "Ci Test"

    def test_me_without_token(self):
        res = client.get(f"{BASE}/auth/me")
        assert res.status_code in (401, 403)  # FastAPI 401 döndürüyor

    def test_logout_invalidates_token(self):
        token = _get_token()
        # Logout
        res = client.post(f"{BASE}/auth/logout", headers=_auth(token))
        assert res.status_code == 200
        # Aynı token artık geçersiz
        res = client.get(f"{BASE}/auth/me", headers=_auth(token))
        assert res.status_code == 401

    def test_check_username_available(self):
        res = client.get(f"{BASE}/auth/check-username/bu_kullanici_kesinlikle_yok_xq9")
        assert res.status_code == 200
        assert res.json()["available"] is True

    def test_check_username_taken(self):
        _get_token()  # ci_test_runner'ı oluştur
        res = client.get(f"{BASE}/auth/check-username/ci_test_runner")
        assert res.status_code == 200
        assert res.json()["available"] is False


# ── CONTAINER TESTLERİ ───────────────────────────────────────────────────────
class TestContainers:

    def setup_method(self):
        """Her test öncesi token al, varsa eski test konteynerini temizle."""
        self.token = _get_token()
        # Önceki testten kalmış konteyner varsa sil
        client.delete(
            f"{BASE}/containers/{TEST_CONTAINER['container_no']}",
            headers=_auth(self.token)
        )

    def teardown_method(self):
        """Her test sonrası test konteynerini ve kullanıcıyı temizle."""
        client.delete(
            f"{BASE}/containers/{TEST_CONTAINER['container_no']}",
            headers=_auth(self.token)
        )

    def test_register_container_success(self):
        res = client.post(
            f"{BASE}/containers/register",
            json=TEST_CONTAINER,
            headers=_auth(self.token),
        )
        assert res.status_code == 201
        data = res.json()["data"]
        assert data["container_no"] == "MSCU9990001"
        assert data["registered_by"] == "Ci Test"

    def test_register_duplicate_container(self):
        client.post(f"{BASE}/containers/register",
                    json=TEST_CONTAINER, headers=_auth(self.token))
        res = client.post(f"{BASE}/containers/register",
                          json=TEST_CONTAINER, headers=_auth(self.token))
        assert res.status_code == 409

    def test_register_bic_mismatch(self):
        body = {**TEST_CONTAINER, "company_name": "MAERSK LINE"}  # MSCU ≠ MAERSK
        res = client.post(f"{BASE}/containers/register",
                          json=body, headers=_auth(self.token))
        assert res.status_code == 409

    def test_list_containers(self):
        client.post(f"{BASE}/containers/register",
                    json=TEST_CONTAINER, headers=_auth(self.token))
        res = client.get(f"{BASE}/containers/list", headers=_auth(self.token))
        assert res.status_code == 200
        nos = [c["container_no"] for c in res.json()["containers"]]
        assert "MSCU9990001" in nos

    def test_list_filter_by_container_no(self):
        client.post(f"{BASE}/containers/register",
                    json=TEST_CONTAINER, headers=_auth(self.token))
        res = client.get(
            f"{BASE}/containers/list?container_no=MSCU999",
            headers=_auth(self.token)
        )
        assert res.status_code == 200
        assert res.json()["total"] >= 1

    def test_delete_container(self):
        client.post(f"{BASE}/containers/register",
                    json=TEST_CONTAINER, headers=_auth(self.token))
        res = client.delete(
            f"{BASE}/containers/MSCU9990001",
            headers=_auth(self.token)
        )
        assert res.status_code == 200
        assert res.json()["status"] == "deleted"

    def test_delete_nonexistent_container(self):
        res = client.delete(
            f"{BASE}/containers/XXXX0000000",
            headers=_auth(self.token)
        )
        assert res.status_code == 404

    def test_bic_map_endpoint(self):
        res = client.get(f"{BASE}/containers/bic-map",
                         headers=_auth(self.token))
        assert res.status_code == 200
        data = res.json()
        assert "MSCU" in data
        assert "TRKU" in data
