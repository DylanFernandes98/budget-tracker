import pytest
from budget import db

@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    # Use a temporary DB instead of the real one
    test_db = tmp_path / "test_budget.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    # Create schema
    db.initialise_database()

    yield db

def test_add_transaction(temp_db):
    temp_db.add_transaction("2025-09-09", 10, "Food", "Lunch")
    result = temp_db.get_all_transactions()
    assert not result.empty
    assert result.iloc[0]["amount"]  == 10
    assert result.iloc[0]["category"]  == "Food"