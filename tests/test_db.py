from budget import db

def test_add_transaction(temp_db):
    """
    Adding a transaction should correctly save it to the database.
    """
    # Add a single transaction into the temporary test database
    temp_db.add_transaction("2025-09-09", 10, "Food", "Lunch")
    
    # Fetch all transactions back from the database
    result = temp_db.get_all_transactions()
    
    # Assert the database is not empty
    assert not result.empty
    # Assert id is 1
    assert result.iloc[0]["id"]  == 1
    # Assert the values match what we inserted
    assert result.iloc[0]["date"]  == "2025-09-09"
    assert result.iloc[0]["amount"]  == 10
    assert result.iloc[0]["category"]  == "Food"
    assert result.iloc[0]["description"]  == "Lunch"

def test_delete_latest_transaction(temp_db):
    """
    delete_latest_transaction should remove only the most recent row.
    """
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

def test_delete_latest_transaction_empty(temp_db):
    """
    Calling delete_latest_transaction on an empty database should return None.
    """
    # Calling delete_latest_transaction on an empty DB should return None
    assert temp_db.delete_latest_transaction() is None

def test_delete_all_transactions(temp_db):
    """
    delete_all_transactions should remove all rows from the database.
    """
    # Add two transactions
    temp_db.add_transaction("2025-09-09", 10, "Food", "Lunch")
    temp_db.add_transaction("2025-09-09", 20, "Drinks", "Bar")

    # Delete all transactions
    temp_db.delete_all_transactions()

    # Fetch transactions back from the database
    result = temp_db.get_all_transactions()
    
    # Assert the database is now empty
    assert result.empty