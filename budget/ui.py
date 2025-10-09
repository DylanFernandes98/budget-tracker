"""
UI module for the Budget Tracker application.

Contains the BudgetApp class, which manages all Tkinter widgets, user input,
database interaction, and embedded Matplotlib graphs.
"""

# --- Core GUI modules ---
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

# --- Date handling ---
from datetime import datetime, date
from tkcalendar import DateEntry

# --- Numerical operations ---
import numpy as np
import pandas as pd

# --- Machine Learning ---
from sklearn.linear_model import LinearRegression

# --- Database functions ---
from .db import (
    initialise_database, add_transaction, get_all_transactions,
    delete_latest_transaction as delete_latest, delete_all_transactions as delete_all,
    get_total_amount
)

# --- Graphing (matplotlib inside Tkinter) ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Type hints (Optional[int] = int or None)
from typing import Optional

class BudgetApp:
    """
    A Tkinter-based GUI application to track expenses.
    Allows adding, displaying and deleting financial transactions with basic validation.
    """    
    def __init__(self, root) -> None:
        self.root = root
        self.canvas: Optional[FigureCanvasTkAgg] = None # Graph canvas; set to None initially so mypy knows type
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
        self.insights_tab = tk.Frame(self.notebook, bg='#D7E3F4')

        # --- Add tabs to the notebook ---
        self.notebook.add(self.transactions_tab, text=" Transactions ")
        self.notebook.add(self.insights_tab, text=" Insights ")

        # --- Build tab contents ---
        self.setup()
        self.setup_insights_tab()

        # --- Populate initial data for Transactions tab
        self.update_transaction_list()
        self.refresh_graph()

    def setup(self):
        """
        Sets up all GUI widgets (input fields, buttons, labels and text area)
        """
        bg_color = '#D7E3F4'

        # --- Left: Add Transaction Form ---
        self.form_frame = tk.LabelFrame(self.transactions_tab, text="Add Transaction", bg=bg_color, padx=12, pady=8)
        self.form_frame.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        # Make left side stretch (1 column for text fields and 1 column for entry fields and buttons)
        self.form_frame.grid_columnconfigure(0, weight=0)
        self.form_frame.grid_columnconfigure(1, weight=1)

        # Welcome label
        self.welcome_label = tk.Label(
            self.form_frame, 
            text="Welcome to my budget tracker app!\n\nAdd your transactions below:", 
            bg=bg_color,
            font=('Segoe UI', 18),
            justify="left",
        )
        self.welcome_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0,12))

        # Input fields
        tk.Label(self.form_frame, text="Date", bg=bg_color).grid(row=1, column=0, sticky="w", padx=10, pady=4)
        self.date_entry = DateEntry(self.form_frame, width=18, date_pattern='dd-mm-yyyy',
                                    maxdate=date.today(), state='readonly')
        self.date_entry.grid(row=1, column=1, sticky="ew", pady=4)

        tk.Label(self.form_frame, text="Amount", bg=bg_color).grid(row=2, column=0, sticky="w", padx=10, pady=4)
        self.amount_entry = tk.Entry(self.form_frame)
        self.amount_entry.grid(row=2, column=1, sticky="ew", pady=4)

        tk.Label(self.form_frame, text="Category", bg=bg_color).grid(row=3, column=0, sticky="w", padx=10, pady=4)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(
            self.form_frame, width=18, textvariable=self.category_var,
            values=['Food', 'Drinks', 'Entertainment', 'Transport', 'Holidays', 'Other'], state='readonly'
        )
        self.category_dropdown.grid(row=3, column=1, sticky="ew", pady=4)

        tk.Label(self.form_frame, text="Description", bg=bg_color).grid(row=4, column=0, sticky="w", padx=10, pady=4)
        self.description_entry = tk.Entry(self.form_frame)
        self.description_entry.grid(row=4, column=1, sticky="ew", pady=4)

        # Status label
        self.status_label  = tk.Label(self.form_frame, text="", bg=bg_color, fg="green", font=('bold', 16))
        self.status_label.grid(row=5, column=1, sticky="ew", pady=4)

        # Buttons
        clear_button = tk.Button(self.form_frame, text="Clear form", command=self.clear_form, fg='white', bg='#A9A9A9')
        clear_button.grid(row=6, column=1, sticky="ew", padx=4, pady=(20,5))

        submit_button = tk.Button(self.form_frame, text="Add Transaction", command=self.submit_transaction,
                                  fg='white', bg='#4CAF50')
        submit_button.grid(row=7, column=1, sticky="ew", padx=4, pady=(5,50))

        delete_button = tk.Button(self.form_frame, text="Delete latest transaction",
                                  command=self.delete_latest_transaction, fg='white', bg='#CD5C5C')
        delete_button.grid(row=8, column=1, sticky="ew", padx=4, pady=(5))

        delete_all_button = tk.Button(self.form_frame, text="Delete all transactions",
                                      command=self.delete_all_transactions, fg='white', bg='#CD5C5C')
        delete_all_button.grid(row=9, column=1, sticky="ew", padx=4, pady=(5,50))

        export_button = tk.Button(self.form_frame, text="Export to CSV",
                                      command=self.export_to_csv, fg='white', bg='#3F51B5')
        export_button.grid(row=10, column=1, sticky="ew", padx=4, pady=(5))

        # --- Right: Transactions and Data Visualisation form ---
        self.right = tk.Frame(self.transactions_tab, bg=bg_color)
        self.right.grid(row=0, column=1, sticky="nsew", padx=(0,16), pady=16)

        # Make right side stretch
        self.right.grid_rowconfigure(0, weight=2)  # Transactions list grows more
        self.right.grid_rowconfigure(1, weight=0)  # Stats fixed height
        self.right.grid_rowconfigure(2, weight=1)  # Graph grows
        self.right.grid_columnconfigure(0, weight=1)

        # Transactions area
        tx_box = tk.LabelFrame(self.right, text="Transactions", bg=bg_color, padx=8, pady=8)
        tx_box.grid(row=0, column=0, sticky="nsew")
        tx_box.grid_rowconfigure(0, weight=1)
        tx_box.grid_columnconfigure(0, weight=1)

        self.text_output = tk.Text(tx_box, height=15, width=60)
        self.text_output.grid(row=0, column=0, sticky="nsew")

        # Stats area
        stats = tk.Frame(self.right, bg=bg_color, padx=8, pady=8)
        stats.grid(row=1, column=0, sticky="ew", pady=(8,8))
        stats.grid_columnconfigure(0, weight=1)
        stats.grid_columnconfigure(1, weight=0)

        self.amount_spent  = tk.Label(stats, text="", bg=bg_color, fg="black", font=('bold', 18))
        self.amount_spent.grid(row=1, column=0, sticky="w")

        self.month_spent   = tk.Label(stats, text="", bg=bg_color, fg="black", font=('bold', 18))
        self.month_spent.grid(row=2, column=0, sticky="w")
        
        self.predict_spent = tk.Label(stats, text="", bg=bg_color, fg="black", font=('bold', 18))
        self.predict_spent.grid(row=3, column=0, sticky="w")

        # Graph area
        self.graph_frame = tk.LabelFrame(self.right, text="Data Visualisation", bg=bg_color, padx=8, pady=8)
        self.graph_frame.grid(row=2, column=0, sticky="nsew")
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)

    def setup_insights_tab(self) -> None:
        pass

    def submit_transaction(self) -> None:
        """
        Validates user input, then saves the transaction to the database and updates the GUI.
        """
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()

        # Ensure all fields are filled (except description)
        if not all([date, amount, category]):
            self.status_label.config(text="All fields must be filled in.", fg="red")
            return

        # Validate amount is a positive number
        try:
            amount = float(amount)
            if amount < 0:
                self.status_label.config(text="Amount must be a positive number.", fg="red")
                return
        except ValueError:
            self.status_label.config(text="Amount must be a number.", fg="red")
            return

        # Validate description is NOT a number
        if description.isnumeric():
            self.status_label.config(text="Description must not be a number.", fg="red")
            return

        # Add transaction and refresh the GUI
        add_transaction(date, amount, category, description)
        self.status_label.config(text="Transaction added successfully.", fg="green")
        self.clear_form(show_status=False) # Keep the transaction message visible
        self.update_transaction_list()

        # Call the function to refresh the graph
        self.refresh_graph()

    def update_transaction_list(self) -> None:
        """
        Fetches all the transactions and updates the display area, total amount spent and monthly average spend.
        """
        df = get_all_transactions()
        self.text_output.delete('1.0', tk.END)
        if df.empty:
            self.text_output.insert(tk.END, "No transactions found.")
        else:
            # Display transactions as a formatted table (no index)
            self.text_output.insert(tk.END, df.to_string(index=False))
        
        # Update total amount spent 
        amount = get_total_amount()
        self.amount_spent.config(text="Total amount spent = £{:.2f}".format(amount))

        # Update average monthly spend
        self.calculate_monthly_avg()

        # Update predicted spend
        self.predict_next_month_spend()

    def calculate_monthly_avg(self) -> None:
        """
        Calculates and displays the average amount spent per month.
        """
        monthly = self._get_monthly_totals()

        if monthly is None or monthly.empty:
            self.month_spent.config(text="Average monthly spend = £0.00")
            return
        
        # Calculate the average monthly spend    
        avg = monthly['amount'].mean()
        self.month_spent.config(text="Average monthly spend = £{:.2f}".format(avg))

    def predict_next_month_spend(self) -> None:
        """
        Predicts the next month's spending using linear regression based on historical monthly totals.
        """
        monthly = self._get_monthly_totals()

        if monthly is None or len(monthly) < 2:
            self.predict_spent.config(text="Next month's predicted spend = Need at least 2 months of data")
            return
        
        # Creates a numeric sequence for months: 0, 1, 2 etc
        monthly['month_num'] = range(len(monthly))

        # Takes the input (month) and output (amount)
        X = monthly[['month_num']]
        y = monthly['amount']
        
        # Initalise a simple linear regression model
        model = LinearRegression()
        model.fit(X, y)

        # Predict for the next month
        next_month = pd.DataFrame([[len(monthly)]], columns=['month_num']) # E.g. if we have 5 months, predict month 5 (zero-indexed)
        prediction = model.predict(next_month)[0] # Get the predicted value from the result array

        self.predict_spent.config(text="Next month's predicted spend = £{:.2f}".format(prediction))

    def clear_form(self, show_status=True) -> None:
        """
        Clears the form.
        """
        if not any([self.date_entry.get(), self.amount_entry.get(), self.category_var.get(), self.description_entry.get()]):
            if show_status:
                self.status_label.config(text="All fields are already clear.", fg="red")
        else:
            self.date_entry.delete(0, tk.END)
            self.amount_entry.delete(0, tk.END)
            self.category_var.set('')
            self.description_entry.delete(0, tk.END)
            if show_status:
                self.status_label.config(text="All fields are clear.", fg="green")

    def delete_latest_transaction(self) -> None:
        """
        Deletes the most recently added transaction (if there is one).
        """
        latest_id = delete_latest()
        if latest_id:
            self.status_label.config(text=f"Transaction with ID {latest_id} deleted.", fg="green")
            self.update_transaction_list()
        else:
            self.status_label.config(text="No transaction to delete.", fg="red")

        # Call the function to refresh the graph
        self.refresh_graph()

    def delete_all_transactions(self) -> None:
        """
        Deletes all the transactions (if there is any).
        """
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all transactions?")
        if confirm:
            delete_all()
            self.status_label.config(text="All transactions have been deleted.", fg="green")
            self.update_transaction_list()
        else:
            self.status_label.config(text="Delete cancelled.", fg="red")

        # Call the function to refresh the graph
        self.refresh_graph()

    def show_transaction_graph(self) -> None:
        """
        Displays a bar chart of the total amount spent per category inside the Tkinter window.
        """
        df = get_all_transactions()
        if df.empty:
            return

        # Destroy old canvas if it exists
        if hasattr(self, 'canvas') and self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Group transactions by category, sum their amounts, and sort from lowest to highest
        grouped = df.groupby('category')['amount'].sum().sort_values()

        # Create a horizontal bar chart figure sized to match the layout
        fig, ax = plt.subplots(figsize=(4.9, 2))
        grouped.plot(kind='barh', ax=ax, color='#4CAF50')

        # Set chart title and axis labels
        ax.set_title('Total Spent per Category')
        ax.set_xlabel('Amount (£)')
        ax.set_ylabel('Category')

        # Add padding to avoid clipping and improve layout
        plt.subplots_adjust(left=0.4, right=0.95, top=0.85, bottom=0.3)

        # Reduce font size of axis tick labels for a cleaner look
        ax.tick_params(labelsize=9)

        # Embed the Matplotlib figure into the Tkinter graph frame
        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        # Ensure the figure is closed to avoid lingering state
        plt.close(fig)

    def refresh_graph(self) -> None:
        """
        Updates or removes the graph whether there is data
        """
        df = get_all_transactions()

        # If there is no data then remove the graph from the GUI
        if df.empty:
            # Destroy old canvas if it exists
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None
            # Update state to reflect no graph is currently visible
            self.graph_visible = False
            return
        
        # If there is data then draw the graph in the GUI
        self.show_transaction_graph()
        self.graph_visible = True

    def _get_monthly_totals(self) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame with monthly total spend.
        Returns None if there's no data.
        """

        df = get_all_transactions()
        if df.empty:
            return None
        
        # Convert 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        df['month'] = df['date'].dt.to_period(freq='M')

        # Group by month and sum amounts, then convert to a clean DataFrame
        return df.groupby('month')['amount'].sum().reset_index()
    
    def export_to_csv(self) -> None:
        """
        Exports all transactions from the database to a CSV file.
        """
        df = get_all_transactions()
        if df.empty:
            return None
        
        # Ask user where to save CSV file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Save transactions as CSV"
        )

        # If user provideda file path, export the DataFrame to CSV
        if file_path:
            df.to_csv(file_path, index=False)