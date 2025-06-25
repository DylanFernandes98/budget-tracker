import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from db import (
    initialise_database, add_transaction, get_all_transactions,
    delete_latest_transaction as delete_latest, delete_all_transactions as delete_all,
    get_total_amount
)

class BudgetApp:
    def __init__(self, root):
        self.root = root
        self.root.option_add('*Font', ('Segoe UI', 11))
        self.root.configure(bg='#D7E3F4')
        self.root.title("Budget Tracker")
        self.setup()
        self.update_transaction_list()
        self.welcome_label.config(text="Welcome to my budget tracker app!", font='bold')

    def setup(self):
        bg_color = '#D7E3F4'

        self.welcome_label = tk.Label(self.root, text="", bg=bg_color)
        self.welcome_label.grid(row=0, column=0, columnspan=3, pady=10)

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

        clear_button = tk.Button(self.root, text="Clear form", command=self.clear_form, fg='white', bg='#6A8CAF')
        clear_button.grid(row=5, column=0, columnspan=3, pady=10)

        delete_button = tk.Button(self.root, text="Delete transaction", command=self.delete_latest_transaction, fg='white', bg='#F08080')
        delete_button.grid(row=6, column=0, pady=10)

        delete_all_button = tk.Button(self.root, text="Delete all transactions", command=self.delete_all_transactions, fg='white', bg='#CD5C5C')
        delete_all_button.grid(row=6, column=1, pady=10)

        submit_button = tk.Button(self.root, text="Add Transaction", command=self.submit_transaction, fg='white', bg='#4CAF50')
        submit_button.grid(row=6, column=2, pady=10)

        self.status_label = tk.Label(self.root, text="", bg=bg_color, fg="green")
        self.status_label.grid(row=7, column=0, columnspan=3)

        self.text_output = tk.Text(self.root, height=15, width=60)
        self.text_output.grid(row=8, column=0, columnspan=3, padx=10, pady=10)

        self.amount_spent = tk.Label(self.root, text="", bg=bg_color, fg="green")
        self.amount_spent.grid(row=9, column=0, columnspan=3)

    def submit_transaction(self):
        date = self.date_entry.get()
        amount = self.amount_entry.get()
        category = self.category_var.get()
        description = self.description_entry.get()

        if not all([date, amount, category, description]):
            self.status_label.config(text="All fields must be filled in.", fg="red")
            return

        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            self.status_label.config(text="Date must be in 'YYYY-MM-DD' format.", fg="red")
            return

        try:
            amount = float(amount)
            if amount < 0:
                self.status_label.config(text="Amount must be a positive number.", fg="red")
                return
        except ValueError:
            self.status_label.config(text="Amount must be a number.", fg="red")
            return

        if category.isnumeric():
            self.status_label.config(text="Category must not be a number.", fg="red")
            return
        if description.isnumeric():
            self.status_label.config(text="Description must not be a number.", fg="red")
            return

        add_transaction(date, amount, category, description)
        self.status_label.config(text="Transaction added successfully.", fg="green")
        self.reset_form()
        self.update_transaction_list()

    def reset_form(self):
        self.date_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_var.set('')
        self.description_entry.delete(0, tk.END)

    def update_transaction_list(self):
        df = get_all_transactions()
        self.text_output.delete('1.0', tk.END)
        if df.empty:
            self.text_output.insert(tk.END, "No transactions found.")
        else:
            self.text_output.insert(tk.END, df.to_string(index=False))
        amount = get_total_amount()
        self.amount_spent.config(text=f"Total amount spent: £{amount:.2f}", fg="green")

    def clear_form(self):
        if not any([self.date_entry.get(), self.amount_entry.get(), self.category_var.get(), self.description_entry.get()]):
            self.status_label.config(text="All fields are already clear.", fg="red")
        else:
            self.reset_form()
            self.status_label.config(text="All fields are clear.", fg="green")

    def delete_latest_transaction(self):
        latest_id = delete_latest()
        if latest_id:
            self.status_label.config(text=f"Transaction with ID {latest_id} deleted.", fg="green")
            self.update_transaction_list()
        else:
            self.status_label.config(text="No transaction to delete.", fg="red")

    def delete_all_transactions(self):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all transactions?")
        if confirm:
            delete_all()
            self.status_label.config(text="All transactions have been deleted.", fg="green")
            self.update_transaction_list()
        else:
            self.status_label.config(text="Delete cancelled.", fg="red")

if __name__ == "__main__":
    initialise_database()
    root = tk.Tk()
    app = BudgetApp(root)
    root.mainloop()
