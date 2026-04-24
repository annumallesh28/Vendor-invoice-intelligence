import streamlit as st
import pandas as pd

from inference.predict_freight import predict_freight_cost

st.title("🚚 Freight Cost Prediction")

st.markdown("""
**Objective:**  
Predict freight cost for a vendor invoice using **Invoice Dollars**  
to support budgeting, forecasting, and vendor negotiations.
""")

with st.form("freight_form"):
    col1, col2 = st.columns(2)

    with col1:
        dollars = st.number_input(
            "💰 Invoice Dollars",
            min_value=1.0,
            value=18500.0
        )
        
    with col2:
        quantity = st.number_input(
            "📦 Invoice Quantity",
            min_value=1,
            value=100
        )

    submit_freight = st.form_submit_button("🔮 Predict Freight Cost")

if submit_freight:
    input_data = {
        "Dollars": [dollars],
        "Quantity": [quantity]
    }

    prediction = predict_freight_cost(input_data)['Predicted_Freight']

    st.success("Prediction completed successfully.")

    st.metric(
        label="📊 Estimated Freight Cost",
        value=f"${prediction[0]:,.2f}"
    )
