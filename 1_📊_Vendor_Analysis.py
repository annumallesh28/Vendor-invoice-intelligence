import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# -------------------------
# Custom CSS for Premium UI
# -------------------------
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background-color: #f9f2d4;
        border: 1px solid #e1d5a3;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] {
        color: #1c2b36;
        font-size: 28px !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #4a5568;
        font-size: 16px !important;
        font-weight: 600;
    }
    h1 {
        text-align: center;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>
""", unsafe_allow_html=True)

st.title("End to End Vendor Insights")

# -------------------------
# Database Connection & Querying
# -------------------------
@st.cache_resource
def get_connection():
    return sqlite3.connect("data/inventory.db", check_same_thread=False)

@st.cache_data
def load_kpis():
    conn = get_connection()

    # Total purchases (cost to business)
    try:
        total_purchase = pd.read_sql(
            "SELECT SUM(Dollars) as val FROM purchases", conn
        ).iloc[0]['val']
    except Exception:
        total_purchase = 0.0

    # Estimated retail sales = end_inventory items sold × retail price
    # Sales Volume = begin onHand - end onHand + purchases received (approx)
    # Simpler: use purchase_prices retail Price × purchases Quantity as "implied retail"
    try:
        implied_sales = pd.read_sql("""
            SELECT SUM(pp.Price * p.Quantity) as val
            FROM purchases p
            JOIN purchase_prices pp ON p.Brand = pp.Brand
        """, conn).iloc[0]['val']
    except Exception:
        implied_sales = 0.0

    # Unsold capital = end inventory onHand × retail Price
    try:
        unsold_capital = pd.read_sql(
            "SELECT SUM(onHand * Price) as val FROM end_inventory", conn
        ).iloc[0]['val']
    except Exception:
        unsold_capital = 0.0

    # Total invoices processed
    try:
        total_invoices = pd.read_sql(
            "SELECT COUNT(*) as val FROM vendor_invoice", conn
        ).iloc[0]['val']
    except Exception:
        total_invoices = 0

    return (
        float(implied_sales) if pd.notnull(implied_sales) else 0.0,
        float(total_purchase) if pd.notnull(total_purchase) else 0.0,
        float(unsold_capital) if pd.notnull(unsold_capital) else 0.0,
        int(total_invoices),
    )

@st.cache_data
def load_chart_data():
    conn = get_connection()

    # Purchase amount by vendor
    try:
        purchases_vendor = pd.read_sql(
            "SELECT VendorName, SUM(Dollars) as TotalPurchase, SUM(Quantity) as TotalQty FROM purchases GROUP BY VendorName",
            conn
        )
    except Exception:
        purchases_vendor = pd.DataFrame({'VendorName': ['N/A'], 'TotalPurchase': [0], 'TotalQty': [0]})

    # Invoice totals by vendor
    try:
        invoice_vendor = pd.read_sql(
            "SELECT VendorName, SUM(Dollars) as InvoiceDollars, SUM(Freight) as TotalFreight, COUNT(*) as InvoiceCount FROM vendor_invoice GROUP BY VendorName",
            conn
        )
    except Exception:
        invoice_vendor = pd.DataFrame({'VendorName': ['N/A'], 'InvoiceDollars': [0], 'TotalFreight': [0], 'InvoiceCount': [0]})

    # Top brands by purchase amount
    try:
        brand_data = pd.read_sql(
            "SELECT Description, SUM(Dollars) as TotalPurchase FROM purchases GROUP BY Description ORDER BY TotalPurchase DESC LIMIT 10",
            conn
        )
    except Exception:
        brand_data = pd.DataFrame({'Description': ['N/A'], 'TotalPurchase': [0]})

    # End inventory by city (top 10)
    try:
        inventory_city = pd.read_sql(
            "SELECT City, SUM(onHand * Price) as InventoryValue FROM end_inventory GROUP BY City ORDER BY InventoryValue DESC LIMIT 10",
            conn
        )
    except Exception:
        inventory_city = pd.DataFrame({'City': ['N/A'], 'InventoryValue': [0]})

    return purchases_vendor, invoice_vendor, brand_data, inventory_city


# -------------------------
# Main Dashboard
# -------------------------
try:
    with st.spinner("Calculating Business Metrics (Querying Database)..."):
        implied_sales, total_purchase, unsold_capital, total_invoices = load_kpis()
        purchases_vendor, invoice_vendor, brand_data, inventory_city = load_chart_data()

    gross_profit = implied_sales - total_purchase
    profit_margin = (gross_profit / implied_sales * 100) if implied_sales > 0 else 0.0

    def format_millions(val):
        if val >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        elif val >= 1_000:
            return f"{val / 1_000:.2f}K"
        return f"{val:.2f}"

    # ---- ROW 1: KPIs ----
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Implied Revenue ($)", format_millions(implied_sales))
    col2.metric("Total Purchases ($)", format_millions(total_purchase))
    col3.metric("Gross Profit ($)", format_millions(gross_profit))
    col4.metric("Profit Margin (%)", f"{profit_margin:.1f}%")
    col5.metric("Unsold Capital ($)", format_millions(unsold_capital))

    st.write("---")

    bar_color = '#e6939b'

    # ---- ROW 2: Charts ----
    # 1. Purchase Contribution Donut (top 7 + others)
    top_purchase_sorted = purchases_vendor.sort_values('TotalPurchase', ascending=False)
    top_7 = top_purchase_sorted.head(7)
    others_sum = top_purchase_sorted.iloc[7:]['TotalPurchase'].sum()
    if others_sum > 0:
        others_row = pd.DataFrame({'VendorName': ['All Others'], 'TotalPurchase': [others_sum], 'TotalQty': [0]})
        donut_data = pd.concat([top_7, others_row], ignore_index=True)
    else:
        donut_data = top_7

    fig_donut = px.pie(
        donut_data, values='TotalPurchase', names='VendorName', hole=0.5,
        title='Purchase Contribution by Vendor (%)',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_donut.update_traces(textinfo='percent', textposition='outside')
    fig_donut.update_layout(showlegend=False, title_x=0.5)

    # 2. Top Vendors by Purchase Amount
    top10_vendors = purchases_vendor.sort_values('TotalPurchase', ascending=False).head(10)
    fig_top_vendors = px.bar(
        top10_vendors.sort_values('TotalPurchase', ascending=True),
        x='TotalPurchase', y='VendorName', orientation='h',
        title='Top 10 Vendors by Purchase Amount',
        color_discrete_sequence=[bar_color]
    )
    fig_top_vendors.update_layout(title_x=0.5, xaxis_title=None, yaxis_title=None)

    # 3. Top Brands by Purchase
    fig_top_brands = px.bar(
        brand_data.sort_values('TotalPurchase', ascending=True),
        x='TotalPurchase', y='Description', orientation='h',
        title='Top 10 Brands by Purchase Amount',
        color_discrete_sequence=[bar_color]
    )
    fig_top_brands.update_layout(title_x=0.5, xaxis_title=None, yaxis_title=None)

    r2c1, r2c2, r2c3 = st.columns([1, 1, 1])
    r2c1.plotly_chart(fig_donut, width='stretch')
    r2c2.plotly_chart(fig_top_vendors, width='stretch')
    r2c3.plotly_chart(fig_top_brands, width='stretch')

    # ---- ROW 3: Charts ----
    # 4. Freight Cost by Vendor (Top 7)
    top_freight = invoice_vendor.sort_values('TotalFreight', ascending=False).head(7)
    fig_freight = px.bar(
        top_freight.sort_values('TotalFreight', ascending=True),
        x='TotalFreight', y='VendorName', orientation='h',
        title='Top Vendors by Freight Cost',
        color_discrete_sequence=['#a8d8ea']
    )
    fig_freight.update_layout(title_x=0.5, xaxis_title=None, yaxis_title=None)

    # 5. Inventory Value by City
    fig_city = px.bar(
        inventory_city.sort_values('InventoryValue', ascending=True),
        x='InventoryValue', y='City', orientation='h',
        title='End Inventory Value by City (Top 10)',
        color_discrete_sequence=['#c7b8ea']
    )
    fig_city.update_layout(title_x=0.5, xaxis_title=None, yaxis_title=None)

    r3c1, r3c2 = st.columns([1, 1])
    r3c1.plotly_chart(fig_freight, width='stretch')
    r3c2.plotly_chart(fig_city, width='stretch')

except Exception as e:
    st.error(f"Could not calculate metrics due to a database/table error: {e}")
    st.exception(e)
