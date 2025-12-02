# --- Standard library ---
from typing import Optional

# --- Tkinter GUI modules ---
import tkinter as tk
from tkinter import ttk

# --- Third-party libraries ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Local mixins ---
from .transactions import TransactionTabMixin
from .insights import InsightsTabMixin

class BudgetApp(TransactionTabMixin, InsightsTabMixin):
    """
    A Tkinter-based GUI application to track expenses.
    Allows adding, displaying and deleting financial transactions with basic validation.
    """    
    def __init__(self, root) -> None:
        self.root = root

        # --- Global Matplotlib styling for consistent graph text ---
        plt.rcParams.update({
            "font.family": "Segoe UI",
            "font.size": 14,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.labelsize": 14,
            "xtick.labelsize": 14,
            "ytick.labelsize": 14,
            "figure.facecolor": "#F8FAFC",
            "axes.facecolor": "#F8FAFC"
        })

        self.canvas: Optional[FigureCanvasTkAgg] = None # Graph canvas; set to None initially so mypy knows type
        self.trend_canvas: Optional[FigureCanvasTkAgg] = None # Trend graph canvas; set to None initially so mypy knows type
        self.pie_canvas: Optional[FigureCanvasTkAgg] = None # Pie graph canvas; set to None initially so mypy knows type
        self.root.option_add('*Font', ('Segoe UI', 14))
        self.root.configure(bg='#D7E3F4')
        self.root.title("Budget Tracker")

        # --- Make the window responsive ---
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # --- Create notebook (tabbed interface) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky='nsew')

        # --- Style the tab labels ---
        style = ttk.Style()
        style.configure('TNotebook.Tab', font=('Segoe UI', 14))

        # --- Create individual tabs ---
        self.transactions_tab = tk.Frame(self.notebook, bg='#D7E3F4')
        self.insights_tab = tk.Frame(self.notebook, bg='#E8F4EA')

        # --- Add tabs to the notebook ---
        self.notebook.add(self.transactions_tab, text=" Transactions ")
        self.notebook.add(self.insights_tab, text=" Insights ")

        # --- Build tab contents ---
        self.setup_transactions_tab()
        self.setup_insights_tab()

        # --- Populate initial data for Transactions tab
        self.update_transaction_list()
        self.refresh_graph()
        self.refresh_insights()