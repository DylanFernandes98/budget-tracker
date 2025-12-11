import pytest
import tkinter as tk
from budget.ui.app import BudgetApp
from budget import db

@pytest.fixture
def app(tmp_path, monkeypatch):
    """
    Shared fixture for creating a temporary BudgetApp instance with isolated DB.
    """
    # Use a temporary DB instead of the real one
    test_db = tmp_path / "test_budget.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    # Initialise the DB schema
    db.initialise_database()

    # Creates headless Tkinter app
    root = tk.Tk()
    root.withdraw()
    app = BudgetApp(root)
    
    yield app # Return the app to the test function
    
    root.destroy() #Close Tkinter window

@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    """
    Creates a fresh temporary database for DB tests.
    """
    # Use a temporary DB instead of the real one
    test_db = tmp_path / "test_budget.db"
    monkeypatch.setattr(db, "DB_NAME", str(test_db))

    # Create schema
    db.initialise_database()

    yield db