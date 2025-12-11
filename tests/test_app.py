from unittest.mock import patch

def test_submit_transaction_valid(app):
    """
    Submitting a valid transaction should call add_transaction
    with correctly formatted values.
    """
    # Set test values
    app.date_entry.set_date('01-07-2025')
    app.amount_entry.insert(0, "20.50")
    app.category_var.set("Food")
    app.description_entry.insert(0, "Groceries")

    # Mock add_transaction so it doesn't write to the real DB
    with patch("budget.ui.transactions.add_transaction") as mock_add_transaction:
        app.submit_transaction()

        # Check that add_transaction was called once with correct args
        mock_add_transaction.assert_called_once_with("2025-07-01", 20.50, "Food", "Groceries")

def test_submit_transaction_invalid_amount(app):
    """
    If the amount field is invalid, add_transaction should NOT be called.
    """
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