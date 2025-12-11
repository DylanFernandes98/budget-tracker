import pandas as pd
from unittest.mock import patch, MagicMock

def test_show_transaction_graph_with_data(app, monkeypatch):
    """
    show_transaction_graph should create, draw, and grid the chart widget
    when valid transaction data exists.
    """
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