import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

# --- Initialize persistent data using session_state ---
def load_or_create(filename, columns):
    path = Path(filename)
    if path.exists():
        return pd.read_csv(path)
    else:
        return pd.DataFrame(columns=columns)

if "purchases" not in st.session_state:
    st.session_state["purchases"] = load_or_create("purchases.csv", ["Date", "Item", "Quantity", "UnitPrice", "Total"])

if "sales" not in st.session_state:
    st.session_state["sales"] = load_or_create("sales.csv", ["Date", "Item", "Quantity", "SellingPrice", "Total"])

if "expenses" not in st.session_state:
    st.session_state["expenses"] = load_or_create("expenses.csv", ["Date", "Category", "Amount"])

def save_all():
    st.session_state["purchases"].to_csv("purchases.csv", index=False)
    st.session_state["sales"].to_csv("sales.csv", index=False)
    st.session_state["expenses"].to_csv("expenses.csv", index=False)

# --- Streamlit UI ---
st.set_page_config(page_title="Inventory Tracker", layout="wide")
st.sidebar.title("Inventory Tracker")
page = st.sidebar.radio("Navigate", ["Purchases", "Sales", "Expenses", "Reports"])

# --- Purchases Page ---
if page == "Purchases":
    st.header("Record Purchase")
    item = st.text_input("Item name")
    qty = st.number_input("Quantity", min_value=0.0, step=0.1)
    price = st.number_input("Unit price", min_value=0.0, step=0.1)
    if st.button("Add Purchase"):
        if item and qty > 0 and price > 0:
            new_row = pd.DataFrame([[date.today(), item, qty, price, qty * price]],
                                   columns=st.session_state["purchases"].columns)
            st.session_state["purchases"] = pd.concat([st.session_state["purchases"], new_row], ignore_index=True)
            save_all()
            st.success("Purchase recorded.")
        else:
            st.warning("Please fill all fields correctly.")
    st.dataframe(st.session_state["purchases"])

# --- Sales Page ---
elif page == "Sales":
    st.header("Record Sale")
    item = st.text_input("Item name")
    qty = st.number_input("Quantity sold", min_value=0.0, step=0.1)
    price = st.number_input("Selling price", min_value=0.0, step=0.1)
    if st.button("Add Sale"):
        if item and qty > 0 and price > 0:
            new_row = pd.DataFrame([[date.today(), item, qty, price, qty * price]],
                                   columns=st.session_state["sales"].columns)
            st.session_state["sales"] = pd.concat([st.session_state["sales"], new_row], ignore_index=True)
            save_all()
            st.success("Sale recorded.")
        else:
            st.warning("Please fill all fields correctly.")
    st.dataframe(st.session_state["sales"])

# --- Expenses Page ---
elif page == "Expenses":
    st.header("Record Expense")
    cat = st.selectbox("Category", ["Employees", "Electricity", "Water", "Rent", "Other"])
    amt = st.number_input("Amount", min_value=0.0, step=0.1)
    if st.button("Add Expense"):
        if amt > 0:
            new_row = pd.DataFrame([[date.today(), cat, amt]], columns=st.session_state["expenses"].columns)
            st.session_state["expenses"] = pd.concat([st.session_state["expenses"], new_row], ignore_index=True)
            save_all()
            st.success("Expense recorded.")
        else:
            st.warning("Amount must be greater than 0.")
    st.dataframe(st.session_state["expenses"])

# --- Reports Page ---
else:
    st.header("Reports")
    total_purchase = st.session_state["purchases"]["Total"].sum()
    total_sales = st.session_state["sales"]["Total"].sum()
    total_expenses = st.session_state["expenses"]["Amount"].sum()
    profit = total_sales - total_purchase - total_expenses

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Purchases", f"${total_purchase:.2f}")
    col2.metric("Total Sales", f"${total_sales:.2f}")
    col3.metric("Total Expenses", f"${total_expenses:.2f}")
    col4.metric("Net Profit", f"${profit:.2f}")

    st.subheader("Stock Summary")
    bought = st.session_state["purchases"].groupby("Item")["Quantity"].sum()
    sold = st.session_state["sales"].groupby("Item")["Quantity"].sum()
    stock = (bought - sold).fillna(0)
    st.dataframe(stock.reset_index().rename(columns={"Quantity": "Remaining"}))

    st.download_button("Download Purchases CSV", st.session_state["purchases"].to_csv(index=False), "purchases.csv")
    st.download_button("Download Sales CSV", st.session_state["sales"].to_csv(index=False), "sales.csv")
    st.download_button("Download Expenses CSV", st.session_state["expenses"].to_csv(index=False), "expenses.csv")
