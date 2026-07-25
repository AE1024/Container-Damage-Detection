"""
Session-scoped fixture: her CI run öncesi/sonrası Atlas'taki stale test verisini temizler.
"""
import pytest


@pytest.fixture(scope="session", autouse=True)
def clean_test_data():
    from core.database import users_col, containers_col
    _clean(users_col, containers_col)
    yield
    _clean(users_col, containers_col)


def _clean(users_col, containers_col):
    # username alanı olan yeni format kullanıcılar
    users_col.delete_many({
        "username": {"$in": ["ci_test_runner", "ci_reg_only", "ci_dup_test"]}
    })
    # username alanı olmayan eski format kullanıcılar (first+last+company ile tespit)
    users_col.delete_many({
        "username": {"$exists": False},
        "first_name": {"$in": ["ci", "reg", "dup"]},
        "company": "TestCompany",
    })
    containers_col.delete_many({"container_no": "MSCU9990001"})
