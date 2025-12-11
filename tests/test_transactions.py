import pytest
import tkinter as tk
import pandas as pd
from unittest.mock import patch, MagicMock
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

def test_show_transaction_graph_with_data(app, monkeypatch):
    # Fake dataframe with 2 rows (so df is NOT empty)
    fake_df = pd.DataFrame({
        "category": ["Food", "Transport"],
        "amount": [10, 20]
    })

    # Make get_all_transactions return fake data
    monkeypatch.setattr("budget.ui.transactions.get_all_transactions", lambda: fake_df)

    # Mock FigureCanvasTkAgg so it doesn't create a real chart
    with patch("budget.ui.transactions.FigureCanvasTkAgg") as mock_canvas_class:
        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        # Mock the tk widget returned by get_tk_widget()
        fake_widget = MagicMock()
        mock_canvas.get_tk_widget.return_value = fake_widget

        # Run the function
        app.show_transaction_graph()

        # Check the canvas was created and drawn
        mock_canvas_class.assert_called_once()
        mock_canvas.draw.assert_called_once()

        # The widget should be gridded inside the frame
        fake_widget.grid.assert_called_once()


