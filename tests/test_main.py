import sys
import os

# Add the parent directory (where main.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tkinter as tk
from unittest.mock import patch
from main import BudgetApp


def test_submit_transaction_valid(monkeypatch):
    # Set up root and app
    root = tk.Tk()
    root.withdraw()  # Hide the GUI window
    app = BudgetApp(root)

    # Set test values
    app.date_entry.set_date('01-07-2025')
    app.amount_entry.insert(0, "20.50")
    app.category_var.set("Food")
    app.description_entry.insert(0, "Groceries")

    # Mock add_transaction so it doesn't write to the real DB
    with patch("main.add_transaction") as mock_add_transaction:
        app.submit_transaction()

        # Check that add_transaction was called once with correct args
        mock_add_transaction.assert_called_once_with("01-07-2025", 20.50, "Food", "Groceries")

    root.destroy()
