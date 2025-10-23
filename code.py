# inventory_app.py
import streamlit as st
import pandas as pd
from datetime import date

# Load or create data
@st.cache_data
def load_data():
    try:
        purchases = pd.read_csv("purchases.csv")
        sales = pd.read_csv("sales.csv")
        expenses = pd.read_csv("expenses.csv")
    except FileNotFoundError:
        purchases = pd.DataFrame(columns=["Date", "Item", "Quantity", "UnitPrice", "Total"])
        sales = pd.DataFrame(columns=["Date", "Item", "Quantity", "SellingPrice", "Total"])
        expenses = pd.DataFrame(columns=["Date", "Category", "Amount"])
    return purchases, sales, expenses

def save_data(purchases, sales, expenses):
    purchases.to_csv("purchases.csv", index=False)
    sales.to_csv("sales.csv", index=False)
    expenses.to_csv("expenses.csv", index=False)

purchases, sales, expenses = load_data()

st.sidebar.title("Inventory Tracker")
page = st.sidebar.radio("Navigate", ["Purchases", "Sales", "Expenses", "Reports"])

# --- Purchases Page ---
if page == "Purchases":
    st.header("Record Purchase")
    item = st.text_input("Item name")
    qty = st.number_input("Quantity", min_value=0.0, step=0.1)
    price = st.number_input("Unit price", min_value=0.0, step=0.1)
    if st.button("Add Purchase"):
        total = qty * price
        new_row = pd.DataFrame([[date.today(), item, qty, price, total]],
                               columns=purchases.columns)
        purchases = pd.concat([purchases, new_row], ignore_index=True)
        save_data(purchases, sales, expenses)
        st.success("Purchase recorded.")
    st.dataframe(purchases)

# --- Sales Page ---
elif page == "Sales":
    st.header("Record Sale")
    item = st.text_input("Item name")
    qty = st.number_input("Quantity sold", min_value=0.0, step=0.1)
    price = st.number_input("Selling price", min_value=0.0, step=0.1)
    if st.button("Add Sale"):
        total = qty * price
        new_row = pd.DataFrame([[date.today(), item, qty, price, total]],
                               columns=sales.columns)
        sales = pd.concat([sales, new_row], ignore_index=True)
        save_data(purchases, sales, expenses)
        st.success("Sale recorded.")
    st.dataframe(sales)

# --- Expenses Page ---
elif page == "Expenses":
    st.header("Record Expense")
    cat = st.selectbox("Category", ["Employees", "Electricity", "Water", "Rent", "Other"])
    amt = st.number_input("Amount", min_value=0.0, step=0.1)
    if st.button("Add Expense"):
        new_row = pd.DataFrame([[date.today(), cat, amt]], columns=expenses.columns)
        expenses = pd.concat([expenses, new_row], ignore_index=True)
        save_data(purchases, sales, expenses)
        st.success("Expense recorded.")
    st.dataframe(expenses)

# --- Reports Page ---
else:
    st.header("Reports")
    total_purchase = purchases["Total"].sum()
    total_sales = sales["Total"].sum()
    total_expenses = expenses["Amount"].sum()
    profit = total_sales - total_purchase - total_expenses

    st.metric("Total Purchases", f"${total_purchase:.2f}")
    st.metric("Total Sales", f"${total_sales:.2f}")
    st.metric("Total Expenses", f"${total_expenses:.2f}")
    st.metric("Net Profit", f"${profit:.2f}")

    st.subheader("Stock Summary")
    bought = purchases.groupby("Item")["Quantity"].sum()
    sold = sales.groupby("Item")["Quantity"].sum()
    stock = (bought - sold).fillna(0)
    st.dataframe(stock.reset_index().rename(columns={0: "Remaining"}))

