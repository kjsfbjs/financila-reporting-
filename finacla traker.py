import streamlit as st
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import xlsxwriter


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def authenticate_user():
    stored_password = hash_password("sahil123")  # Default password
    entered_password = st.text_input("Enter password to access dashboard", type="password")
    if hash_password(entered_password) == stored_password:
        return True
    else:
        st.error("Incorrect password! Access denied.")
        return False


def generate_excel_report(df):
    excel_file = "financial_report.xlsx"
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Raw Data", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Raw Data"]

        # Format Header
        header_format = workbook.add_format({"bold": True, "bg_color": "#4F81BD", "font_color": "white", "border": 1})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Auto-adjust column width
        for col_num, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
            worksheet.set_column(col_num, col_num, max_length)

        # Conditional Formatting
        money_format = workbook.add_format({"num_format": "$#,##0.00"})
        worksheet.set_column("B:D", None, money_format)
        worksheet.conditional_format("D2:D100", {"type": "3_color_scale"})

        # Create Pivot Table Sheet
        pivot_sheet = workbook.add_worksheet("Summary")
        pivot_sheet.write("A1", "Monthly Financial Summary", header_format)
        pivot_table = df.pivot_table(index="Month", values=["Income", "Expenses", "Savings"], aggfunc="sum")
        pivot_table.to_excel(writer, sheet_name="Summary", startrow=2)

    return excel_file


def main():
    st.title("Personal Finance Tracker 💰")

    if not authenticate_user():
        return  # Stop execution if authentication fails

    st.success("Login Successful! Welcome to the dashboard.")

    # Currency Selection
    base_currency = st.selectbox("Select your currency", ["USD", "EUR", "INR", "GBP", "AUD", "CAD"])

    # Income Section
    st.header("Income Sources")
    num_sources = st.number_input("Number of income sources", min_value=1, step=1)
    income_sources = {}
    total_income = 0

    for i in range(num_sources):
        source = st.text_input(f"Income Source {i + 1}")
        amount = st.number_input(f"Amount from {source}", min_value=0.0, step=0.01)
        income_sources[source] = amount
        total_income += amount

    # Expenses Section
    st.header("Expenses")
    num_expenses = st.number_input("Number of expenses", min_value=1, step=1)
    expenses = {}
    total_expenses = 0

    for i in range(num_expenses):
        category = st.text_input(f"Expense Category {i + 1}")
        amount = st.number_input(f"Amount for {category}", min_value=0.0, step=0.01)
        expenses[category] = expenses.get(category, 0) + amount
        total_expenses += amount

    savings = total_income - total_expenses

    st.subheader("Financial Summary")
    st.write(f"**Total Income:** {base_currency} {total_income:.2f}")
    st.write(f"**Total Expenses:** {base_currency} {total_expenses:.2f}")
    st.write(f"**Total Savings:** {base_currency} {savings:.2f}")

    # Data Storage
    current_month = datetime.now().strftime("%Y-%m")
    try:
        df = pd.read_csv("financial_data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Month", "Income", "Expenses", "Savings"])

    new_entry = pd.DataFrame([[current_month, total_income, total_expenses, savings]],
                             columns=["Month", "Income", "Expenses", "Savings"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv("financial_data.csv", index=False)

    # Generate Excel Report
    excel_file = generate_excel_report(df)

    # Download Button
    with open(excel_file, "rb") as f:
        st.download_button("Download Financial Report", f, file_name="financial_report.xlsx")

    # Financial Trend Analysis
    st.subheader("Financial Trend Analysis 📊")
    if len(df) > 1:
        X = np.arange(len(df)).reshape(-1, 1)
        y = df["Savings"].values
        model = LinearRegression()
        model.fit(X, y)
        future_months = np.arange(len(df), len(df) + 3).reshape(-1, 1)
        predicted_savings = model.predict(future_months)

        fig, ax = plt.subplots()
        ax.plot(df["Month"], df["Savings"], label="Actual Savings", marker='o')
        ax.plot([f"Month {i + 1}" for i in range(1, 4)], predicted_savings, label="Predicted Savings",
                linestyle="dashed")
        ax.legend()
        st.pyplot(fig)
    else:
        st.write("Not enough data for trend analysis.")


if __name__ == "__main__":
    main()
