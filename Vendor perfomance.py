#!/usr/bin/env python
# coding: utf-8

# In[1]:


# importing required libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns 
import warnings
import sqlite3
from scipy.stats import ttest_ind
import scipy.stats as stats
warnings.filterwarnings('ignore')


# # ingesting data from the database
# conn = sqlite3.connect('inventory.db')

# In[3]:


# inspecting the first few rows
df = pd.read_sql("SELECT * FROM final_table",conn)
df.head(5)


# - Before this, we looked at the different tables in our database to identify key variables, understand their relationships, and determine which ones should be included in the final analysis
# 
# - Now, in this EDA phase, we will analyze the resultant table to gain insights into the distribution of each column. This will help us understand data patterns, identify anomalies, and ensure data quality before proceeding with further analysis.

# In[154]:


df.describe().T


# In[155]:


numeric_cols = df.select_dtypes(include='number').columns

plt.figure(figsize=(15,10))
for i, col in enumerate(numeric_cols):
    plt.subplot(4,4,i+1)
    sns.histplot(df[col], kde=True, bins=30)
    plt.title(col)
plt.tight_layout()
plt.show()


# In[156]:


plt.figure(figsize=(15,10))
for i, col in enumerate(numeric_cols):
    plt.subplot(4,4,i+1)
    sns.boxplot(y = df[col])
    plt.title(col)
plt.tight_layout()
plt.show()


# ### Summary Statistics Insights:
# 
# Negative & Zero Values:
# 
# - Gross Profit: Minimum value is -52,002.78, indicating losses. Some products or transactions may be selling at a loss due to high costs or selling at discounts lower than the purchase price..
# 
# - Profit Margin: Has a minimum of −∞, which suggests cases where revenue is zero or even lower than costs.
# 
# - Total Sales Quantity & Sales Dollars: Minimum values are 0, me aning some products were purchased but never sold. These could be slow-moving or obsolete stock.
# 
# Outliers Indicated by High Standard Deviations:
# 
# - Purchase & Actual Prices: The max values (5,681.81 & 7,499.99) are significantly higher than the mean (24.39 & 35.64), indicating potential premium products.
# 
# - Freight Cost: Huge variation, from 0.09 to 257,032.07, suggests logistics inefficiencies or bulk shipments.
# 
# - Stock Turnover: Ranges from 0 to 274.5, implying some products sell extremely fast while others remain in stock indefinitely. Value more than 1 indicates that Sold quantity for that product is higher than purchased quantity due to either sales are being fulfilled from older stock.

# In[157]:


# filtering inconsistencies
df = pd.read_sql("""
    SELECT * FROM final_table
    WHERE GrossProffit > 0
      AND ProfitMargin > 0
      AND TotalSalesQuantity > 0
""", conn)


# In[158]:


df


# In[159]:


categorical_cols = ["VendorName","Description"]

plt.figure(figsize=(12,5))
for i, col in enumerate(categorical_cols):
    plt.subplot(1,2,i+1)
    sns.countplot(y=df[col], order=df[col].value_counts().index[:10])
    plt.title(f"Count Plot of {col}")
plt.tight_layout()
plt.show()


# In[160]:


# correlation Heatmap
plt.figure(figsize=(12,8))
correlation_matrix = df[numeric_cols].corr()
sns.heatmap(correlation_matrix, annot= True, fmt=".2f",cmap="coolwarm",linewidths=0.5)
plt.title("Correlation Heatmap")
plt.show()


# ## Correlation Insights
# 
# - PurchasePrice has weak correlations with TotalSalesDollars (-0.012) and GrossProfit (-0.016), suggesting that price variations do not significantly impact sales revenue or profit.
# 
# - Strong correlation between total purchase quantity and total sales quantity (0.999), confirming efficient inventory turnover.
# 
# - Negative correlation between profit margin & total sales price (-0.179) suggests that as sales price increases, margins decrease, possibly due to competitive pricing pressures.
# 
# - StockTurnover has weak negative correlations with both GrossProfit (-0.038) and ProfitMargin (-0.055), indicating that faster turnover does not necessarily result in higher profitability.

# ## Buisness Analysis
# - Identify Brands that needs Promotional or Pricing Adjustments which exhibit lower sales performance but higher profit margins

# In[161]:


brand_perfomance = df.groupby('Description').agg({
    'TotalSalesDollars':'sum',
    'ProfitMargin':'mean'}).reset_index()


# In[162]:


low_sales_threshold = brand_perfomance['TotalSalesDollars'].quantile(0.15)
high_margin_threshold = brand_perfomance['ProfitMargin'].quantile(0.85)


# In[163]:


low_sales_threshold


# In[164]:


high_margin_threshold


# In[165]:


# filter brands with low sales but high profit margins
target_brands = brand_perfomance[
    (brand_perfomance['TotalSalesDollars'] <= low_sales_threshold) &
    (brand_perfomance['ProfitMargin'] >= high_margin_threshold)
]

print("Brands with Low Sales but High Profit Margins:")
display(target_brands.sort_values('TotalSalesDollars'))


# In[166]:


brand_perfomance = brand_perfomance[brand_perfomance['TotalSalesDollars'] < 10000] # for better visualization


# In[167]:


plt.figure(figsize=(10, 6))

sns.scatterplot(data=brand_perfomance, x='TotalSalesDollars', y='ProfitMargin', color='blue', label="All Brands", alpha = 0.2)
sns.scatterplot(data=target_brands, x='TotalSalesDollars', y='ProfitMargin', color='red', label="Target Brands")

plt.axhline(high_margin_threshold, linestyle='--', color='black', label="High Margin Threshold")
plt.axvline(low_sales_threshold, linestyle='--', color='black', label="Low Sales Threshold")

plt.xlabel("Total Sales ($)")
plt.ylabel("Profit Margin (%)")
plt.title("Brands for Promotional or Pricing Adjustments")
plt.legend()
plt.grid(True)
plt.show()


# ### Which Vendors & Brands demonstrate the Highest Sales Perfomance?

# In[168]:


def format_dollars(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.2f}K"
    else:
        return str(value)


# In[169]:


# Top vendors & brands by sales Perfomance
top_vendors = df.groupby("VendorName")["TotalSalesDollars"].sum().nlargest(10)
top_brands = df.groupby("Description")["TotalSalesDollars"].sum().nlargest(10)


# In[170]:


top_vendors


# In[171]:


top_brands


# In[172]:


top_brands.apply(lambda x : format_dollars(x))


# In[173]:


plt.figure(figsize=(15, 5))

# Plot for Top Vendors
plt.subplot(1, 2, 1)
ax1 = sns.barplot(y=top_vendors.index, x=top_vendors.values, palette="Blues_r")
plt.title("Top 10 Vendors by Sales")

for bar in ax1.patches:
    ax1.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             format_dollars(bar.get_width()),
             ha='left', va='center', fontsize=10, color='black')

# Plot for Top Brands
plt.subplot(1, 2, 2)
ax2 = sns.barplot(y=top_brands.index.astype(str), x=top_brands.values, palette="Reds_r")
plt.title("Top 10 Brands by Sales")

for bar in ax2.patches:
    ax2.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             format_dollars(bar.get_width()),
             ha='left', va='center', fontsize=10, color='black')

plt.tight_layout()
plt.show()


# ### Which vendors contribute the most total purchase dollars ?

# In[174]:


vendor_perfomance = df.groupby('VendorName').agg({
    'TotalPurchaseDollars': 'sum',
    'GrossProffit': 'sum',
    'TotalSalesDollars': 'sum'
}).reset_index()


# In[175]:


# Calculate total purchase for all vendors
total_purchase = vendor_perfomance['TotalPurchaseDollars'].sum()


# In[176]:


# Compute each vendor's contribution to total purchase
vendor_perfomance['PurchaseContribution%'] = vendor_perfomance['TotalPurchaseDollars'] / total_purchase


# In[177]:


vendor_perfomance = vendor_perfomance.round(2)


# In[178]:


vendor_performance = round(vendor_perfomance.sort_values('PurchaseContribution%', ascending = False), 2)


# In[179]:


# Sort by contribution
vendor_performance = round(vendor_perfomance.sort_values('PurchaseContribution%', ascending=False), 2)

# Pick top 10 vendors
top_vendors = vendor_performance.head(10)

# Format dollar columns
top_vendors['TotalSalesDollars'] = top_vendors['TotalSalesDollars'].apply(format_dollars)
top_vendors['TotalPurchaseDollars'] = top_vendors['TotalPurchaseDollars'].apply(format_dollars)
top_vendors['GrossProffit'] = top_vendors['GrossProffit'].apply(format_dollars)

# Convert contribution to percentage (without % sign)
top_vendors['PurchaseContribution%'] = top_vendors['PurchaseContribution%'].apply(lambda x: round(x * 100, 2))

# Show table
top_vendors


# In[180]:


top_vendors['Cumulative_Contribution%'] = top_vendors['PurchaseContribution%'].cumsum()

fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar plot for Purchase Contribution%
sns.barplot(x=top_vendors['VendorName'], 
            y=top_vendors['PurchaseContribution%'], 
            palette="mako", 
            ax=ax1)

# Add value labels on bars (formatted to 1 decimal place, no % sign)
for i, value in enumerate(top_vendors['PurchaseContribution%']):
    ax1.text(i, value - 1, f"{value:.1f}", ha='center', fontsize=10, color='white')

# Line Plot for Cumulative Contribution%
ax2 = ax1.twinx()
ax2.plot(top_vendors['VendorName'], 
         top_vendors['Cumulative_Contribution%'], 
         color='red', marker='o', linestyle='dashed', label='Cumulative Contribution%')

# Labels and styling
ax1.set_xticklabels(top_vendors['VendorName'], rotation=90)
ax1.set_ylabel('Purchase Contribution %', color='blue')
ax2.set_ylabel('Cumulative Contribution %', color='red')
ax1.set_xlabel('Vendors')
ax1.set_title('Pareto Chart: Vendor Contribution to Total Purchases')

# Optional horizontal line at 100%
ax2.axhline(y=100, color='gray', linestyle='dashed', alpha=0.7)
ax2.legend(loc='upper right')

plt.tight_layout()
plt.show()


# ### How Much of total procurement is dependent on top vendors ?

# In[184]:


print(f"Total Purchase Contribution of top 10 vendors is {round(top_vendors['PurchaseContribution%'].sum(), 2)} %")


# In[ ]:


# Step 1: Calculate total purchase from all vendors
total_purchase_all = vendor_performance['TotalPurchaseDollars'].sum()

# Step 2: Get top 10 vendors by purchase amount
top_vendors = vendor_performance.nlargest(10, 'TotalPurchaseDollars').copy()

# Step 3: Calculate each vendor's contribution percentage (out of all vendors)
top_vendors['Purchase_Contribution%'] = (top_vendors['TotalPurchaseDollars'] / total_purchase_all) * 100

# Step 4: Add "Other Vendors" slice
total_top_10_contribution = top_vendors['Purchase_Contribution%'].sum()
remaining_contribution = 100 - total_top_10_contribution

vendors = list(top_vendors['VendorName'].values)
purchase_contributions = list(top_vendors['Purchase_Contribution%'].values)

vendors.append("Other Vendors")
purchase_contributions.append(remaining_contribution)

# Step 5: Plot donut chart
fig, ax = plt.subplots(figsize=(8, 8))
wedges, texts, autotexts = ax.pie(
    purchase_contributions,
    labels=vendors,
    autopct='%1.1f%%',
    startangle=140,
    pctdistance=0.85,
    colors=plt.cm.Set3.colors  # Change palette if needed
)

# Add white center circle for donut effect
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

# Add total annotation in center
plt.text(0, 0, f"Top 10 Total:\n{total_top_10_contribution:.2f}%", fontsize=14, fontweight='bold', ha='center', va='center')

plt.title("Top 10 Vendor's Purchase Contribution (%)")
plt.tight_layout()
plt.show()


# ### Does purcahsing in Bulk reduce the unit price and what is the optimal purchase volume for cost savings ?

# In[191]:


df['UnitPurchasePrice'] = df['TotalPurchaseDollars'] / df['TotalPurchaseQuantity']


# In[192]:


df["OrderSize"] = pd.qcut(df["TotalPurchaseQuantity"], q=3, labels=["Small", "Medium", "Large"])


# In[194]:


df.groupby('OrderSize')[['UnitPurchasePrice']].mean()


# - Vendors buying in bulk (Large Order Size) get the lowest unit price ($10.78 per unit), meaning higher margins if they can manage inventory efficiently.
# 
# - The price difference between Small and Large orders is substantial (~72% reduction in unit cost).
# 
# - This suggests that bulk pricing strategies successfully encourage vendors to purchase in larger volumes, leading to higher overall sales despite lower per-unit revenue.

# ### How much capital is locked in unsold inventory per vendor, and which vendors contribute the most to it?

# In[195]:


df['UnsoldInventoryValue'] = (df['TotalPurchaseQuantity'] - df['TotalSalesQuantity']) * df['PurchasePrice']
print(f'Total Unsold Capital:', format_dollars(df['UnsoldInventoryValue'].sum()))


# In[196]:


# Aggregate Capital Locked Per Vendor
inventory_value_per_vendor = df.groupby('VendorName')['UnsoldInventoryValue'].sum().reset_index()

# Sort Vendors with the Highest Locked Capital
inventory_value_per_vendor = inventory_value_per_vendor.sort_values(by="UnsoldInventoryValue", ascending=False)
inventory_value_per_vendor['UnsoldInventoryValue'] = inventory_value_per_vendor['UnsoldInventoryValue'].apply(format_dollars)
inventory_value_per_vendor.head(10)


# ### What is the 95% confidence intervals for profit margins of top-performing and low-performing vendors

# In[204]:


top_threshold = df["TotalSalesDollars"].quantile(0.75)
low_threshold = df["TotalSalesDollars"].quantile(0.25)

top_vendors = df[df["TotalSalesDollars"] >= top_threshold]["ProfitMargin"].dropna()
low_vendors = df[df["TotalSalesDollars"] <= low_threshold]["ProfitMargin"].dropna()

top_vendors


# In[205]:


low_vendors


# In[210]:


# 1. Confidence Interval Function
def confidence_interval(data, confidence=0.95):
    mean_val = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(len(data))
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(data) - 1)
    margin_of_error = t_critical * std_err
    return mean_val, mean_val - margin_of_error, mean_val + margin_of_error


# In[211]:


# 2. Get Confidence Intervals
top_mean, top_lower, top_upper = confidence_interval(top_vendors)
low_mean, low_lower, low_upper = confidence_interval(low_vendors)

# 3. Print like the screenshot
print(f"Top Vendors 95% CI: ({top_lower:.2f}, {top_upper:.2f}), Mean: {top_mean:.2f}")
print(f"Low Vendors 95% CI: ({low_lower:.2f}, {low_upper:.2f}), Mean: {low_mean:.2f}")

# 4. Combined Histogram Plot (Overlayed)
plt.figure(figsize=(12, 6))
sns.histplot(top_vendors, kde=True, color='blue', bins=30, alpha=0.5, label='Top Vendors')
sns.histplot(low_vendors, kde=True, color='red', bins=30, alpha=0.5, label='Low Vendors')

# Top Vendor lines
plt.axvline(top_lower, color='blue', linestyle='--', label=f"Top Lower: {top_lower:.2f}")
plt.axvline(top_upper, color='blue', linestyle='--', label=f"Top Upper: {top_upper:.2f}")
plt.axvline(top_mean, color='blue', linestyle='-', label=f"Top Mean: {top_mean:.2f}")

# Low Vendor lines
plt.axvline(low_lower, color='red', linestyle='--', label=f"Low Lower: {low_lower:.2f}")
plt.axvline(low_upper, color='red', linestyle='--', label=f"Low Upper: {low_upper:.2f}")
plt.axvline(low_mean, color='red', linestyle='-', label=f"Low Mean: {low_mean:.2f}")

plt.title("Confidence Interval Comparison: Top vs. Low Vendors (Profit Margin)")
plt.xlabel("Profit Margin (%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


# 

# 
# - The confidence interval for low-performing vendors (40.48% to 42.62%) is significantly higher than that of top-performing vendors (30.74% to 31.61%).
# 
# - This suggests that vendors with lower sales tend to maintain higher profit margins, potentially due to premium pricing or lower operational costs.
# 
# - For High-Performing Vendors: If they aim to improve profitability, they could explore selective price adjustments, cost optimization, or bundling strategies.
# 
# - For Low-Performing Vendors: Despite higher margins, their low sales volume might indicate a need for better marketing, competitive pricing, or improved distribution strategies.

# ### Is there a significant difference in profit margins between top-performing and low-performing vendors?
# 
# Hypothesis:
# 
# - H₀ (Null Hypothesis): There is no significant difference in the mean profit margins of top-performing and low-performing vendors.
# - H₁ (Alternative Hypothesis): The mean profit margins of top-performing and low-performing vendors are significantly different.

# In[212]:


top_threshold = df["TotalSalesDollars"].quantile(0.75)
low_threshold = df["TotalSalesDollars"].quantile(0.25)

top_vendors = df[df["TotalSalesDollars"] >= top_threshold]["ProfitMargin"].dropna()
low_vendors = df[df["TotalSalesDollars"] <= low_threshold]["ProfitMargin"].dropna()

# Perform Two-Sample T-Test
t_stat, p_value = ttest_ind(top_vendors, low_vendors, equal_var=False)

# Print results
print(f"T-Statistic: {t_stat:.4f}, P-Value: {p_value:.4f}")
if p_value < 0.05:
    print("Reject H₀: There is a significant difference in profit margins between top and low-performing vendors.")
else:
    print("Fail to Reject H₀: No significant difference in profit margins.")


# In[213]:


# 1. Connect to the database
conn = sqlite3.connect("inventory.db")

# 2. Load the final_table into a DataFrame
df = pd.read_sql("SELECT * FROM final_table", conn)

# 3. Export to CSV
df.to_csv("final_table.csv", index=False)

# 4. Close the connection
conn.close()

