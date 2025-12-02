"""
Main entrypoint for the Budget Tracker application.

- Initialises the database
- Starts the Tkinter GUI
- Maximises the window on Windows systems
"""

# --- Standard library ---
import platform
import tkinter as tk

# --- Local application modules ---
from budget.db import initialise_database
from budget.ui.app import BudgetApp

if __name__ == "__main__":
    # Initialise the DB and start the application
    initialise_database()
    root = tk.Tk()
    app = BudgetApp(root)

    if platform.system() == 'Windows':
        root.state('zoomed')

    root.mainloop()