# --- Core GUI modules ---
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

# --- Date handling ---
from datetime import date
from tkcalendar import DateEntry

# --- Numerical operations ---
import pandas as pd

# --- Machine Learning ---
from sklearn.linear_model import LinearRegression

# --- Database functions ---
from ..db import (
    initialise_database, add_transaction, get_all_transactions,
    delete_latest_transaction as delete_latest, delete_all_transactions as delete_all,
    get_total_amount
)

# --- Graphing (matplotlib inside Tkinter) ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- Type hints ---
from typing import Callable, Optional

class InsightsTabMixin:
    """
    Contains all code for the Insights tab:
    - layout for the insights tab
    - monthly trend line chart
    - category pie chart
    - top categories list
    - insight summary messages
    """
    # --- Attributes coming from BudgetApp (parent class) ---
    update_transaction_list: Callable  # type: ignore[attr-defined]
    amount_spent: tk.Label  # type: ignore[attr-defined]
    month_spent: tk.Label  # type: ignore[attr-defined]
    predict_spent: tk.Label  # type: ignore[attr-defined]

    trend_canvas: FigureCanvasTkAgg | None  # type: ignore[assignment]
    pie_canvas: FigureCanvasTkAgg | None  # type: ignore[assignment]

    insights_tab: tk.Frame  # type: ignore[attr-defined]

    def setup_insights_tab(self) -> None:
        """
        Sets up the analytics/insights tab layout
        """
        bg_color = '#E8F4EA'

        # --- Main container for everything on the Insights tab ---
        frame = tk.Frame(self.insights_tab, bg=bg_color) # type: ignore[attr-defined]
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        # --- Title ---
        title = tk.Label(
            frame,
            text="Monthly Insights",
            bg=bg_color,
            font=('Segoe UI', 20, 'bold')
        )
        title.pack(pady=(0, 20))

        # --- KPI Row (Top) ---
        self.kpi_frame = tk.Frame(frame, bg=bg_color)
        self.kpi_frame.pack(fill="x", pady=10)

        self.total_label = tk.Label(self.kpi_frame, text="Total spent: £0.00", bg=bg_color, font=('Segoe UI', 18, 'bold'))
        self.total_label.grid(row=0, column=0, padx=20)
        
        self.avg_label = tk.Label(self.kpi_frame, text="Avg monthly: £0.00", bg=bg_color, font=('Segoe UI', 18, 'bold'))
        self.avg_label.grid(row=0, column=1, padx=20)
        
        self.pred_label = tk.Label(self.kpi_frame, text="Predicted next month: £0.00", bg=bg_color, font=('Segoe UI', 18, 'bold'))
        self.pred_label.grid(row=0, column=2, padx=20)

        # --- Chart Area (side by side layout) ---
        charts_frame = tk.Frame(frame, bg=bg_color)
        charts_frame.pack(fill="both", expand=True, pady=10)

        # Trend Chart (left)
        self.trend_frame = tk.LabelFrame(charts_frame, text="📈 Monthly Spending Trend", bg=bg_color, padx=8, pady=8)
        self.trend_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Pie Chart (right)
        self.pie_frame = tk.LabelFrame(charts_frame, text="🥧 Spending by Category", bg=bg_color, padx=8, pady=8)
        self.pie_frame.pack(side="left", fill="both", expand=True)

        # --- Top Categories (below charts) ---
        self.top_frame = tk.LabelFrame(frame, text="Top 3 Categories", bg=bg_color, padx=8, pady=8)
        self.top_frame.pack(fill="x", pady=(0, 10))

        self.top_label = tk.Label(self.top_frame, text="No data yet.", bg=bg_color, font=("Segoe UI", 13))
        self.top_label.pack(anchor="w")

        # --- Insights Text Section ---
        self.text_frame = tk.LabelFrame(frame, text="Insights", bg=bg_color, padx=12, pady=8)
        self.text_frame.pack(fill="x", pady=(10, 0))

        self.insight_text = tk.Label(self.text_frame, text="No insights yet.", bg=bg_color, font=('Segoe UI', 14))
        self.insight_text.pack(anchor="w")

    def refresh_insights(self) -> None:
        """
        Syncs KPI text from Transactions tab to the Insights tab.
        """
        self.update_transaction_list() # type: ignore[attr-defined]
        self.total_label.config(text=self.amount_spent.cget("text")) # type: ignore[attr-defined]
        self.avg_label.config(text=self.month_spent.cget("text")) # type: ignore[attr-defined]
        self.pred_label.config(text=self.predict_spent.cget("text")) # type: ignore[attr-defined]
        
        # Fetch data once
        df = get_all_transactions()
        if df.empty:
            return
        
        monthly = self._get_monthly_totals(df)

        self.show_monthly_trend(df)
        self.show_category_pie(df)
        self.show_top_categories(df)

        if monthly is None or len(monthly) < 2:
            msg = "Add more transactions to see spending trends."
        else:
            last, prev = monthly["amount"].iloc[-1], monthly["amount"].iloc[-2]
            change = last - prev
            pct = abs(change / prev * 100)
            if change > 0:
                msg = f"Spending increased by {pct:.0f}% vs last month - try reviewing your big categories."
            elif change < 0:
                msg = f"Spending decreased by {pct:.0f}% - nice work staying on track!"
            else:
                msg = "Spending stayed the same as last month."

        self.insight_text.config(text=msg)

    def show_monthly_trend(self, df) -> None:
        """
        Displays a line chart of total amount spent per month in the Insights tab
        """
        monthly = self._get_monthly_totals(df)
        if monthly is None or monthly.empty:
            return
        
        # Destroy old canvas if it exists
        if self.trend_canvas:
            self.trend_canvas.get_tk_widget().destroy()

        # Convert month period to string for plotting
        monthly['month'] = monthly['month'].astype(str)

        # Create a larger, cleaner figure
        fig, ax = plt.subplots(figsize=(6.5, 3.5))
        ax.plot(
            monthly['month'], monthly['amount'],
            marker='o', markersize=8, linewidth=3, color='#2E8B57',
            markerfacecolor='#4CAF50', markeredgecolor='black'
        )

        # --- Add subtle style tweaks ---
        ax.set_title('Monthly Spending Trend')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Spent (£)')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, linestyle='--', alpha=0.4)

        plt.subplots_adjust(left=0.15, right=0.98, top=0.88, bottom=0.28)

        # Embed the Matplotlib figure into the Tkinter chart frame
        self.trend_canvas = FigureCanvasTkAgg(fig, master=self.trend_frame)
        self.trend_canvas.draw()
        self.trend_canvas.get_tk_widget().pack(fill="both", expand=True)

        # Ensure the figure is closed to avoid lingering state
        plt.close(fig)

    def show_category_pie(self, df) -> None:
        """
        Displays a pie chart of spending by category in the Insights tab
        """
        if df.empty:
            return
        
        # Destroy old canvas if it exists
        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()

        grouped = df.groupby("category")["amount"].sum()
        fig, ax = plt.subplots(figsize=(3.5, 3.5))

        ax.pie(grouped, labels=grouped.index, autopct="%1.0f%%", startangle=90, colors=plt.cm.Set3.colors, labeldistance=1.1) # type: ignore[attr-defined]
        ax.set_title("Spending by Category")

        # Embed the Matplotlib figure into the Tkinter chart frame
        self.pie_canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Ensure the figure is closed to avoid lingering state
        plt.close(fig)

    def show_top_categories(self, df) -> None:
        """
        Displays top 3 categories by total spend in the Insights tab.
        """
        if df.empty:
            return

        # Calculate top 3 categories
        grouped = df.groupby("category")["amount"].sum().sort_values(ascending=False).head(3)

        # Build a numbered list of the top 3 categories and their total amounts
        lines = []
        for i, (category, amount) in enumerate(grouped.items(), start=1):
            line = f"{i}. {category}: £{amount:.2f}"
            lines.append(line)

        top_text = "\n".join(lines)

        # Destroy old label if it exists
        if self.top_label:
            self.top_label.destroy()

        # Create a label that's *properly left-aligned*
        self.top_label = tk.Label(
            self.top_frame,
            text=top_text,
            bg="#E8F4EA",
            font=("Segoe UI", 14),
            justify="left",   # Ensures all lines align left
            anchor="w"        # Keeps it anchored to the left edge
        )
        self.top_label.pack(anchor="w", pady=(6, 0))

    def _get_monthly_totals(self, df) -> Optional[pd.DataFrame]:
        """
        Returns a DataFrame with monthly total spend.
        Returns None if there's no data.
        """
        if df.empty:
            return None
        
        df = df.copy()
        
        # Convert 'date' column to datetime format
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        df['month'] = df['date'].dt.to_period('M')

        # Group by month and sum amounts, then convert to a clean DataFrame
        return df.groupby('month')['amount'].sum().reset_index()