import pytest
import tkinter as tk
from unittest.mock import patch
from budget.ui.app import BudgetApp
from budget import db

# Fixture for setting up the Tkinter app
@pytest.fixture
def app(tmp_path, monkeypatch):
    # Use a temporary DB instead of the real one
    test_db = tmp_path / "test_budget.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    # Initialise the DB schema
    db.initialise_database()

    root = tk.Tk() # Creates the Tkinter window
    root.withdraw() # Hide GUI window
    app = BudgetApp(root) #Create app with that window
    yield app # Return the app to the test function
    root.destroy() #Close Tkinter window

# Valid transaction test
def test_submit_transaction_valid(app):
    # Set test values
    app.date_entry.set_date('01-07-2025')
    app.amount_entry.insert(0, "20.50")
    app.category_var.set("Food")
    app.description_entry.insert(0, "Groceries")

    # Mock add_transaction so it doesn't write to the real DB
    with patch("budget.ui.transactions.add_transaction") as mock_add_transaction:
        app.submit_transaction()

        # Check that add_transaction was called once with correct args
        mock_add_transaction.assert_called_once_with("01-07-2025", 20.50, "Food", "Groceries")

# Invalid transaction test
def test_submit_transaction_invalid_amount(app):
    # Set test values
    app.date_entry.set_date('01-07-2025')
    app.amount_entry.insert(0, "") # Invalid empty amount
    app.category_var.set("Food")
    app.description_entry.insert(0, "Groceries")

    # Mock add_transaction so it doesn't write to the real DB
    with patch("budget.ui.transactions.add_transaction") as mock_add_transaction:
        app.submit_transaction()

    # Check that the add transaction was NOT called
    mock_add_transaction.assert_not_called()