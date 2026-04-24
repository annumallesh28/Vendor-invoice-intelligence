import streamlit as st


st.title("💡 Executive Business Insights")
st.markdown("Automated strategic takeaways derived from historic vendor and inventory analysis.")

st.divider()

col1, col2 = st.columns(2)

with col1:
    st.header("🔍 Key Exploratory Findings")
    
    with st.expander("1. Brands for Promotional & Pricing Adjustments", expanded=True):
        st.write("""
        **Finding:** 198 brands exhibit lower sales volumes but maintain significantly higher profit margins.  
        **Action:** These brands would heavily benefit from targeted marketing, promotional discounts, or price optimizations to increase sales volume without compromising overall profitability.
        """)
        
    with st.expander("2. Vendor Dependency & Sales Contribution", expanded=True):
        st.write("""
        **Finding:** The top 10 vendors contribute **65.69% of total purchases**, while the remaining vendors comprise only 34.31%.  
        **Risk:** This over-reliance on a few select vendors introduces high supply chain vulnerability.  
        **Action:** Diversify vendor partnerships to mitigate bottleneck risks.
        """)
        
    with st.expander("3. Impact of Bulk Purchasing", expanded=True):
        st.write("""
        **Finding:** Vendors executing bulk purchasing strategies achieve a **72% lower unit cost** ($10.78 per unit compared to smaller orders).  
        **Action:** Leverage this bulk pricing edge to maintain competitive market pricing while padding inventory margins.
        """)

with col2:
    st.header("📉 Financial & Margin Analytics")

    with st.expander("4. Low Inventory Turnover & Capital Lockup", expanded=True):
        st.error("""
        **Finding:** A massive **$2.71M** is currently tied up in Unsold Inventory Capital.  
        **Risk:** Slow-moving inventory skyrockets storage costs and strangles cash flow efficiency.  
        **Action:** Optimize slow-moving inventory by adjusting future purchase quantites, triggering clearance sales, or revising storage policies.
        """)
        
    with st.expander("5. Margin Paradox: High vs. Low Performers", expanded=True):
        st.info("""
        * **Top Vendors' Mean Profit Margin:** 31.17%
        * **Low Vendors' Mean Profit Margin:** 41.55%
        
        **Finding:** Low-performing vendors maintain significantly higher margins but struggle heavily with moving actual sales volume.  
        **Action:** High-margin/Low-volume vendors require better market reach and distribution strategies. Meanwhile, Top-selling vendors should focus explicitly on raw cost efficiency since their margins are naturally tighter.
        """)
        
st.divider()

st.header("🎯 Final Recommendations")
st.markdown("""
1. **Re-evaluate pricing** for low-sales, high-margin brands to aggressively boost volume.
2. **Diversify vendor partnerships** immediately to reduce critical supply chain dependency.
3. **Double down on bulk purchasing** advantages to slash unit costs safely.
4. **Liquidate slow-moving inventory** via clearance to free up the trapped $2.71M in capital.
""")
