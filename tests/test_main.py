from unittest.mock import patch, MagicMock
from budget.main import run_app

def test_run_app_starts_gui():
    """
    Basic test that run_app() starts the GUI correctly.
    """

    with patch("budget.main.initialise_database") as mock_init_db, \
         patch("budget.main.tk.Tk") as mock_tk, \
         patch("budget.main.BudgetApp") as mock_app, \
         patch("budget.main.platform.system", return_value="Windows"):

        # Fake Tk root and app objects
        fake_root = MagicMock()
        fake_app = MagicMock()

        mock_tk.return_value = fake_root
        mock_app.return_value = fake_app

        # Call function
        root, app = run_app()

        # Assertions
        mock_init_db.assert_called_once()
        mock_tk.assert_called_once()
        mock_app.assert_called_once_with(fake_root)

        fake_root.state.assert_called_once_with("zoomed")
        fake_root.mainloop.assert_called_once()

        assert root is fake_root
        assert app is fake_app