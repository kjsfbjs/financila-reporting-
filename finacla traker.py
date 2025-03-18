import streamlit as st
import hashlib
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from fpdf import FPDF


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


def generate_pdf_report(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 20)
    pdf.cell(200, 10, "Personal Finance Report - Sahil", ln=True, align="C")
    pdf.ln(10)

    # Summary Section
    latest_entry = df.iloc[-1]
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Financial Summary", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Month: {latest_entry['Month']}", ln=True)
    pdf.cell(200, 10, f"Total Income: ${latest_entry['Income']:.2f}", ln=True)
    pdf.cell(200, 10, f"Total Expenses: ${latest_entry['Expenses']:.2f}", ln=True)
    pdf.cell(200, 10, f"Total Savings: ${latest_entry['Savings']:.2f}", ln=True)
    pdf.ln(10)

    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 10, "Thank you for using Personal Finance Tracker! - Developed by Sahil", ln=True, align="C")

    pdf_file = "financial_report.pdf"
    pdf.output(pdf_file)
    return pdf_file


def main():
    st.title("📊 Personal Finance Tracker - Developed by Sahil")

    if not authenticate_user():
        return  # Stop execution if authentication fails

    st.success("✅ Login Successful! Welcome to Sahil's dashboard.")

    # Currency Selection
    base_currency = st.selectbox("🌎 Select Your Currency", ["USD", "EUR", "INR", "GBP", "AUD", "CAD"])

    # Month Selection for Planning
    current_month = datetime.now().strftime("%B %Y")
    selected_month = st.text_input("📅 Enter Month (e.g., March 2025)", current_month)

    # Income Section
    st.header("💰 Income Sources")
    num_sources = st.number_input("Number of Income Sources", min_value=1, step=1)
    total_income = 0

    income_sources = {}
    for i in range(num_sources):
        source = st.text_input(f"Income Source {i + 1}")
        amount = st.number_input(f"Amount from {source}", min_value=0.0, step=0.01)
        income_sources[source] = amount
        total_income += amount

    # Expenses Section
    st.header("🛒 Expenses")
    num_expenses = st.number_input("Number of Expenses", min_value=1, step=1)
    total_expenses = 0

    expenses = {}
    for i in range(num_expenses):
        category = st.text_input(f"Expense Category {i + 1}")
        amount = st.number_input(f"Amount for {category}", min_value=0.0, step=0.01)
        expenses[category] = expenses.get(category, 0) + amount
        total_expenses += amount

    savings = total_income - total_expenses

    # Financial Summary
    st.subheader("📌 Financial Summary")
    st.write(f"📅 **Month:** {selected_month}")
    st.write(f"💵 **Total Income:** {base_currency} {total_income:.2f}")
    st.write(f"💸 **Total Expenses:** {base_currency} {total_expenses:.2f}")
    st.write(f"💰 **Total Savings:** {base_currency} {savings:.2f}")

    # Data Storage
    try:
        df = pd.read_csv("financial_data.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["Month", "Income", "Expenses", "Savings"])

    new_entry = pd.DataFrame([[selected_month, total_income, total_expenses, savings]],
                             columns=["Month", "Income", "Expenses", "Savings"])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv("financial_data.csv", index=False)

    # Generate PDF Report
    pdf_file = generate_pdf_report(df)

    # Download Button
    with open(pdf_file, "rb") as f:
        st.download_button("📥 Download Financial Report", f, file_name="financial_report.pdf")

    # Bar Chart for Savings Distribution
    st.subheader("📊 Financial Overview")
    categories = ["Income", "Expenses", "Savings"]
    values = [total_income, total_expenses, savings]
    colors = ["#4CAF50", "#FF5733", "#3498DB"]

    fig, ax = plt.subplots()
    ax.bar(categories, values, color=colors)
    ax.set_ylabel("Amount ($)")
    ax.set_title("Income, Expenses, and Savings Distribution - Sahil")
    st.pyplot(fig)


if __name__ == "__main__":
    main()