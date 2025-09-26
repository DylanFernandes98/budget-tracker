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
    # Add a single transaction into the temporary test database
    temp_db.add_transaction("2025-09-09", 10, "Food", "Lunch")
    # Fetch all transactions back from the database
    result = temp_db.get_all_transactions()
    # Assert the database is not empty
    assert not result.empty
    # Assert the values match what we inserted
    assert result.iloc[0]["id"]  == 1
    assert result.iloc[0]["date"]  == "2025-09-09"
    assert result.iloc[0]["amount"]  == 10
    assert result.iloc[0]["category"]  == "Food"
    assert result.iloc[0]["description"]  == "Lunch"

def test_delete_latest_transaction(temp_db):
    # Add two transactions, so we can test deleting the most recent
    temp_db.add_transaction("2025-09-09", 10, "Food", "Lunch")
    temp_db.add_transaction("2025-09-09", 20, "Drinks", "Bar")
    # Get all transactions, latest should be index 1
    result = temp_db.get_all_transactions()
    latest_id = result.iloc[1]["id"]
    # Delete latest transaction and check it matches latest index of 1
    deleted_id = temp_db.delete_latest_transaction()
    assert deleted_id == latest_id
    # After deletion, only first transaction should remain
    remaining = temp_db.get_all_transactions()
    assert len(remaining) == 1 # Only 1 row left
    assert remaining.iloc[0]["id"] != latest_id # Ensure deleted row is gone