# dashboard.py
import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px
from main import process_receipt
from parse_receipt import save_to_json

st.set_page_config(page_title="Receipt Analyzer", layout="centered")
st.title("Receipt Analyzer")

# File uploader
uploaded_file = st.file_uploader("Upload a Receipt Image", type=["jpg", "jpeg", "png"])

temp_path = "temp_receipt.png"

if uploaded_file:
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    st.image(temp_path, caption="Uploaded Receipt", use_container_width=True)
    st.info("Processing...")

    try:
        receipt_data = process_receipt(temp_path)

        st.success("Receipt Processed!")
        st.subheader("Extracted Details")
        st.json(receipt_data)

        if st.button("Save to receipts.json"):
            save_to_json(receipt_data, filename="receipts.json")
            st.success("Receipt saved successfully!")

    except Exception as e:
        st.error(f"Error: {str(e)}")

    # Option to delete uploaded receipt image
    if st.button("Delete Uploaded Receipt", type="primary"):
        if os.path.exists(temp_path):
            os.remove(temp_path)
            st.success("Uploaded receipt deleted.")
            st.rerun()

# View saved receipts
st.markdown("---")
st.subheader("Receipt History")

receipts = []
if os.path.exists("receipts.json"):
    with open("receipts.json", "r") as f:
        receipts = json.load(f)

    if receipts:
        for i, r in enumerate(receipts[::-1]):
            display_index = len(receipts) - 1 - i  # original index in list
            with st.expander(f"Receipt #{len(receipts) - i} — {r.get('date', 'N/A')}"):
                st.json(r)
                if st.button(f"Delete Receipt #{len(receipts) - i}", key=f"delete_{display_index}"):
                    receipts.pop(display_index)
                    with open("receipts.json", "w") as f:
                        json.dump(receipts, f, indent=2)
                    st.success("Receipt deleted successfully.")
                    st.rerun()
    else:
        st.info("No saved receipts yet.")
else:
    st.info("No saved receipts yet.")

# Insights Section
st.markdown("---")
st.subheader("Spending Insights")

if receipts:
    rows = []
    for receipt in receipts:
        date = receipt.get("date", "Unknown")
        for item in receipt.get("items", []):
            name_lower = item["name"].strip().lower()
            if name_lower in ["total", "subtotal", "change", "cash"]:
                continue
            rows.append({
                "Date": date,
                "Item": item["name"],
                "Category": item.get("category", "Uncategorized"),
                "Amount": item["price"]
            })

    df = pd.DataFrame(rows)

    if not df.empty:
        cat_totals = df.groupby("Category")["Amount"].sum().reset_index()

        st.write("Total Spend by Category")
        st.bar_chart(cat_totals.set_index("Category"))

        fig = px.pie(cat_totals, values='Amount', names='Category',
                     title='Expense Distribution by Category')
        st.plotly_chart(fig)

        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        time_trend = df.groupby("Date")["Amount"].sum().reset_index().dropna()

        if not time_trend.empty:
            st.write("Spending Trend Over Time")
            st.line_chart(time_trend.set_index("Date"))
    else:
        st.info("No item data available for plotting.")
else:
    st.info("Upload and save receipts to see spending insights.")