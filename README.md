# 💰 Budget Tracker App

A simple personal finance tracker built with Python. This desktop app lets you record income and expenses, view transactions, and keep track of your budget in real time. It features a minimal interface built with Tkinter, uses SQLite for data storage, and includes both a dynamic bar chart to visualize spending by category and a prediction tool to estimate next month’s spending.

## 🖼️ Preview

![App Screenshot](./screenshot.JPG)

## ✨ Features

- Add transaction expense with date, category, amount, and description  
- View all transactions in a scrollable interface
- Predict next month’s spending using basic linear regression on past data
- See the current balance, monthly average, and next month predicted spend update in real time
- Chart updates live when transactions are added or deleted
- Data is stored locally using SQLite  
- Built with a clean, minimal GUI using Tkinter  

## 🛠 Tech Stack

- Python 3  
- Tkinter - User Interface  
- SQLite - Persistent Local Storage
- Pandas - Data Handling and Display
- Matplotlib – Graph Visualisation
- Scikit-learn – Machine Learning

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/DylanFernandes98/budget-tracker.git
   cd budget-tracker
2. **Run the application**
   ```bash
   python main.py

