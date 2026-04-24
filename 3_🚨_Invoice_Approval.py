import streamlit as st
import pandas as pd

from inference.predict_invoice_flag import predict_invoice_flag

st.title("🚨 Invoice Manual Approval Prediction")

st.markdown("""
**Objective:**  
Predict whether a vendor invoice should be **flagged for manual approval**  
based on abnormal cost, freight, or delivery patterns.
""")

with st.form("invoice_flag_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        invoice_quantity = st.number_input(
            "Invoice Quantity",
            min_value=1,
            value=50
        )
        freight = st.number_input(
            "Freight Cost",
            min_value=0.0,
            value=1.73
        )

    with col2:
        invoice_dollars = st.number_input(
            "Invoice Dollars",
            min_value=1.0,
            value=352.95
        )
        total_item_quantity = st.number_input(
            "Total Item Quantity",
            min_value=1,
            value=162
        )

    with col3:
        total_item_dollars = st.number_input(
            "Total Item Dollars",
            min_value=1.0,
            value=2476.0
        )

    submit_flag = st.form_submit_button("🧠 Evaluate Invoice Risk")

if submit_flag:
    input_data = {
        "invoice_quantity": [invoice_quantity],
        "invoice_dollars": [invoice_dollars],
        "Freight": [freight],
        "total_item_quantity": [total_item_quantity],
        "total_item_dollars": [total_item_dollars]
    }
    
    try:
        flag_prediction = predict_invoice_flag(input_data)['Predicted_Flag']
        is_flagged = bool(flag_prediction[0])
        
        if is_flagged:
            st.error("🚨 Invoice requires **MANUAL APPROVAL**")
        else:
            st.success("✅ Invoice is **SAFE for Auto-Approval**")
    except Exception as e:
        st.error(f"Prediction failed: {e}")
