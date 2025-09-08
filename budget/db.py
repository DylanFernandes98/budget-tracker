# --- Database and DataFrame modules
import sqlite3
import pandas as pd

def initialise_database():
    """
    Creates the SQLite database and a 'transactions' table if it doesn't already exist.
    """
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

def add_transaction(date, amount, category, description):
    """
    Inserts a new transaction record into the database.
    """
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (date, amount, category, description)
            VALUES (?, ?, ?, ?)
        ''', (date, amount, category, description))
        conn.commit()

def get_all_transactions():
    """
    Retrieves all transactions from the database as a pandas DataFrame.
    Returns the dataframe with all transaction records, ordered by date descending.
    """
    with sqlite3.connect('budget.db') as conn:
        return pd.read_sql('SELECT * FROM transactions ORDER BY date DESC', conn)

def delete_latest_transaction():
    """
    Deletes the most recently added transaction from the database.
    Returns int or None (ID of the deleted transaction or None if there are no records).
    """
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

def delete_all_transactions():
    """
    Deletes all transaction records from the database.
    """
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()

def get_total_amount():
    """
    Calculates the total sum of all transaction amounts.
    Returns float or None (Total amount spent or 0.0 if no records exist.)
    """
    with sqlite3.connect('budget.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0.0