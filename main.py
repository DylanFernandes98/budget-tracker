import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import (
    initialise_database, add_transaction, get_all_transactions,
    delete_latest_transaction as delete_latest, delete_all_transactions as delete_all,
    get_total_amount
)

class BudgetApp:
    """
    A Tkinter-based GUI application to track expenses.
    Allows adding, displaying and deleting financial transactions with basic validation.
    """    
    def __init__(self, root):
        self.root = root
        self.root.option_add('*Font', ('Segoe UI', 11))
        self.root.configure(bg='#D7E3F4')
        self.root.title("Budget Tracker")
        
        self.setup() # Initialise the GUI layout
        self.update_transaction_list() # Populate the data
        self.welcome_label.config(text="Welcome to my budget tracker app!", font='bold')

    def setup(self):
        """
        Sets up all GUI widgets (input fields, buttons, labels and text area)
        """
        bg_color = '#D7E3F4'

        # --- Welcome Label ---
        self.welcome_label = tk.Label(self.root, text="", bg=bg_color)
        self.welcome_label.grid(row=0, column=0, columnspan=3, pady=10)

        # --- Input Fields ---
        tk.Label(self.root, text="Date (YYYY-MM-DD)", bg=bg_color).grid(row=1, column=0)
        self.date_entry = tk.Entry(self.root)
        self.date_entry.grid(row=1, column=1)

        tk.Label(self.root, text="Amount", bg=bg_color).grid(row=2, column=0)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=2, column=1)

        tk.Label(self.root, text="Category", bg=bg_color).grid(row=3, column=0)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(self.root, width=18, textvariable=self.category_var,
            values=['Food', 'Drinks', 'Entertainment', 'Transport', 'Holidays', 'Other'], state='readonly')
        self.category_dropdown.grid(row=3, column=1)

        tk.Label(self.root, text="Description", bg=bg_color).grid(row=4, column=0)
        self.description_entry = tk.Entry(self.root)
        self.description_entry.grid(row=4, column=1)

        # --- Buttons ---
        clear_button = tk.Button(self.root, text="Clear form", command=self.clear_form, fg='white', bg='#6A8CAF')
        clear_button.grid(row=5, column=0, columnspan=3, pady=10)

        delete_button = tk.Button(self.root, text="Delete transaction", command=self.delete_latest_transaction, fg='white', bg='#F08080')
        delete_button.grid(row=6, column=0, pady=10)

        delete_all_button = tk.Button(self.root, text="Delete all transactions", command=self.delete_all_transactions, fg='white', bg='#CD5C5C')
        delete_all_button.grid(row=6, column=1, pady=10)

        submit_button = tk.Button(self.root, text="Add Transaction", command=self.submit_transaction, fg='white', bg='#4CAF50')
        submit_button.grid(row=6, column=2, pady=10)

        # --- Status and Output Area ---
        self.status_label = tk.Label(self.root, text="", bg=bg_color, fg="green")
        self.status_label.grid(row=7, column=0, columnspan=3)

        self.text_output = tk.Text(self.root, height=15, width=60)
        self.text_output.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.amount_spent = tk.Label(self.root, text="", bg=bg_color, fg="black", font='bold')
        self.amount_spent.grid(row=9, column=0, columnspan=3, pady=10)

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

        # Validate the date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            self.status_label.config(text="Date must be in 'YYYY-MM-DD' format.", fg="red")
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

    def update_transaction_list(self):
        """
        Fetches all the transactions and updates the display area and total amount spent.
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

if __name__ == "__main__":
    # Initialise the DB and start the application
    initialise_database()
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()