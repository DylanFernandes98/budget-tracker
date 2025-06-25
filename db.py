import sqlite3
import pandas as pd

# Function to initialise the database and table
def initialise_database():
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY,
                date TEXT,
                amount REAL,
                category TEXT,
                description TEXT
            )
        ''')

# Add a transaction
def add_transaction(date, amount, category, description):
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, amount, category, description)
            VALUES (?, ?, ?, ?)
        ''', (date, amount, category, description))
        conn.commit()

# Get all transactions as a DataFrame
def get_all_transactions():
    with sqlite3.connect('budget.db') as conn:
        return pd.read_sql('SELECT * FROM transactions ORDER BY date DESC', conn)

# Delete the most recent transaction
def delete_latest_transaction():
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM transactions")
        result = cursor.fetchone()
        if result and result[0] is not None:
            latest_id = result[0]
            cursor.execute("DELETE FROM transactions WHERE id = ?", (latest_id,))
            conn.commit()
            return latest_id
        return None

# Delete all transactions
def delete_all_transactions():
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()

# Get total of all amounts
def get_total_amount():
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0.0
