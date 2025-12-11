import pandas as pd
from unittest.mock import patch, MagicMock

def test_show_monthly_trend_with_data(app, monkeypatch):
    """
    When valid data exists, show_monthly_trend should create and draw a chart
    and pack the widget into the UI.
    """
    # Fake dataframe with 2 months of spending
    fake_df = pd.DataFrame({
        "date": ["2025-01-10", "2025-02-15"],
        "amount": [100, 200],
        "category": ["Food", "Transport"]
    })

    # Make get_all_transactions return this fake data
    monkeypatch.setattr("budget.ui.insights.get_all_transactions", lambda: fake_df)

    # Mock _get_monthly_totals to avoid relying on date parsing logic
    fake_monthly = pd.DataFrame({
        "month": ["2025-01", "2025-02"],
        "amount": [100, 200]
    })
    monkeypatch.setattr(app, "_get_monthly_totals", lambda df: fake_monthly)

    # Mock the chart canvas so no real Matplotlib figure is created
    with patch("budget.ui.insights.FigureCanvasTkAgg") as mock_canvas_class:
        mock_canvas = MagicMock()
        mock_canvas_class.return_value = mock_canvas

        fake_widget = MagicMock()
        mock_canvas.get_tk_widget.return_value = fake_widget

        # Call the function under test
        app.show_monthly_trend(fake_df)

        # Asserts
        mock_canvas_class.assert_called_once()  # A chart must be created
        mock_canvas.draw.assert_called_once()   # Chart must be drawn
        fake_widget.pack.assert_called_once()   # Widget must be added to UI