# --- Detecting OS ---
import platform

# --- Core GUI modules ---
import tkinter as tk
from tkinter import ttk, messagebox

# --- Numerical operations ---
import numpy as np
import pandas as pd

# --- Date handling ---
from datetime import datetime, date
from tkcalendar import DateEntry

# --- Database functions ---
from db import (
    initialise_database, add_transaction, get_all_transactions,
    delete_latest_transaction as delete_latest, delete_all_transactions as delete_all,
    get_total_amount
)
# --- Graphing (matplotlib inside Tkinter) ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class BudgetApp:
    """
    A Tkinter-based GUI application to track expenses.
    Allows adding, displaying and deleting financial transactions with basic validation.
    """    
    def __init__(self, root):
        self.root = root
        self.root.option_add('*Font', ('Segoe UI', 14))
        self.root.configure(bg='#D7E3F4')
        self.root.title("Budget Tracker")

        #--- Main centered frame ---
        self.main_frame = tk.Frame(self.root, bg='#D7E3F4')
        self.main_frame.pack(pady=20) 

        self.graph_visible = False # Tracks whether graph is currently visible
        
        self.setup() # Initialise the GUI layout

        self.update_transaction_list() # Populate the data
        self.refresh_graph()
        self.welcome_label.config(text="Welcome to my budget tracker app!", font='bold', pady=20)

    def setup(self):
        """
        Sets up all GUI widgets (input fields, buttons, labels and text area)
        """
        bg_color = '#D7E3F4'

        # --- Welcome Label ---
        self.welcome_label = tk.Label(self.main_frame, text="", bg=bg_color)
        self.welcome_label.grid(row=0, column=0, columnspan=3, pady=10)

        # --- Input Fields ---
        tk.Label(self.main_frame, text="Date", bg=bg_color).grid(row=1, column=0)
        self.date_entry = DateEntry(self.main_frame, width=18, date_pattern='dd-mm-yyyy', maxdate=date.today(), state='readonly')
        self.date_entry.grid(row=1, column=1)

        tk.Label(self.main_frame, text="Amount", bg=bg_color).grid(row=2, column=0)
        self.amount_entry = tk.Entry(self.main_frame)
        self.amount_entry.grid(row=2, column=1)

        tk.Label(self.main_frame, text="Category", bg=bg_color).grid(row=3, column=0)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.main_frame, width=18, textvariable=self.category_var,
            values=['Food', 'Drinks', 'Entertainment', 'Transport', 'Holidays', 'Other'], state='readonly')
        self.category_dropdown.grid(row=3, column=1)

        tk.Label(self.main_frame, text="Description", bg=bg_color).grid(row=4, column=0)
        self.description_entry = tk.Entry(self.main_frame)
        self.description_entry.grid(row=4, column=1)

        # --- Buttons ---
        clear_button = tk.Button(self.main_frame, text="Clear form", command=self.clear_form, fg='white', bg='#6A8CAF')
        clear_button.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

        delete_button = tk.Button(self.main_frame, text="Delete latest transaction", command=self.delete_latest_transaction, fg='white', bg='#F08080')
        delete_button.grid(row=6, column=0, padx=10, pady=10)

        delete_all_button = tk.Button(self.main_frame, text="Delete all transactions", command=self.delete_all_transactions, fg='white', bg='#CD5C5C')
        delete_all_button.grid(row=6, column=1, padx=10, pady=10)

        submit_button = tk.Button(self.main_frame, text="Add Transaction", command=self.submit_transaction, fg='white', bg='#4CAF50')
        submit_button.grid(row=6, column=2, padx=10, pady=10)

        # Use 'self' to access button later in toggle transaction graph function
        self.graph_button = tk.Button(self.main_frame, text="Show Graph", command=self.toggle_transaction_graph)
        self.graph_button.grid(row=11, column=2, pady=10)

        # --- Status and Output Area ---
        self.status_label = tk.Label(self.main_frame, text="", bg=bg_color, fg="green")
        self.status_label.grid(row=7, column=0, columnspan=3)

        self.text_output = tk.Text(self.main_frame, height=15, width=60)
        self.text_output.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.month_spent = tk.Label(self.main_frame, text="", bg=bg_color, fg="black", font='bold')
        self.month_spent.grid(row=9, column=0, columnspan=3, pady=10)

        self.amount_spent = tk.Label(self.main_frame, text="", bg=bg_color, fg="black", font='bold')
        self.amount_spent.grid(row=10, column=0, columnspan=3, pady=10)

        # --- Graph Area ---
        self.graph_frame = tk.Frame(self.main_frame, bg='#D7E3F4')
        self.graph_frame.grid(row=12, column=0, columnspan=3, pady=10)

    def submit_transaction(self):
        """
        Validates user input, then saves the transaction to the database and updates the GUI.
        """
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()

        # Ensure all fields are filled
        if not all([date, amount, category, description]):
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

    def update_transaction_list(self):
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
        self.amount_spent.config(text="Total amount spent: £{:.2f}".format(amount))

        # Update average monthly spend
        self.calculate_monthly_avg()

    def calculate_monthly_avg(self):
        """
        Calculates and displays the average amount spent per month
        """
        df = get_all_transactions()
        if df.empty:
            self.month_spent.config(text="Average monthly spend: £0.00")
            return
        
        # Convert 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period(freq='M')
        # Calculate the average monthly spend    
        monthly_totals = df.groupby('month')['amount'].sum().values
        avg = np.mean(monthly_totals)

        self.month_spent.config(text="Average monthly spend: £{:.2f}".format(avg))

    def clear_form(self, show_status=True):
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

    def delete_latest_transaction(self):
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

    def delete_all_transactions(self):
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

    def show_transaction_graph(self):
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
        self.canvas.get_tk_widget().pack()

        # Ensure the figure is closed to avoid lingering state
        plt.close(fig)
    
    def toggle_transaction_graph(self):
        """
        Toggles the transaction graph so the user can show or hide it.
        """
        # Hide the graph
        if self.graph_visible:
            # Destroy old canvas if it exists
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()
            self.graph_button.config(text="Show Graph")
            self.graph_visible = False
        # Show the graph
        else:
            self.show_transaction_graph()
            self.graph_button.config(text="Hide Graph")
            self.graph_visible = True

    def refresh_graph(self):
        """
        Updates or removes the graph whether there is data
        """
        df = get_all_transactions()

        if self.graph_visible:
            # Destroy old canvas if it exists
            if hasattr(self, 'canvas') and self.canvas:
                self.canvas.get_tk_widget().destroy()

        if df.empty:
            self.graph_visible = False
            self.graph_button.config(text="Show Graph", state="disabled")

        else:
            self.show_transaction_graph()
            self.graph_button.config(state="normal")

if __name__ == "__main__":
    # Initialise the DB and start the application
    initialise_database()
    root = tk.Tk()
    app = BudgetApp(root)

    if platform.system() == 'Windows':
        root.state('zoomed')

    root.mainloop()