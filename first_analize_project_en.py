import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import re # For more complex string operations if needed

# --- II. Python Environment Setup and Data Loading ---

# B. Load Data
# Assuming CSV files are in the same directory as the script

transaction_data_raw = pd.ExcelFile("QVI_transaction_data.xlsx")
customer_data = pd.read_csv('QVI_purchase_behaviour.csv')

# Create a copy for manipulation, keeping the original data intact
transaction_data = transaction_data_raw.parse('in')

print("--- Initial Information of Transaction Data ---")
transaction_data.info()
print("\n--- First 5 rows of Transaction Data ---")
print(transaction_data.head())

print("\n--- Initial Information of Customer Data ---")
customer_data.info()
print("\n--- First 5 rows of Customer Data ---")
print(customer_data.head())

# --- III. Transaction Data: Preprocessing and Exploratory Analysis ---

# A. Convert Date Column (DATE)
print("\n--- Converting DATE column ---")
# The original code had transaction_data = pd.to_datetime(transaction_data, origin='1899-12-30', unit='D')
# This attempts to convert the entire DataFrame. We need to specify the 'DATE' column.
transaction_data['DATE'] = pd.to_datetime(transaction_data['DATE'], origin='1899-12-30', unit='D')
print(f"Data type of DATE column after conversion: {transaction_data['DATE'].dtype}")
print(transaction_data['DATE'].head()) # Accessing the 'DATE' column for head()

# B. Analyze Product Name Column (`PROD_NAME`)
print("\n--- Analyzing PROD_NAME ---")
# 1. Check unique product names (example)
print("Some product names and their counts:")
# The original code was transaction_data.value_counts().head() which is incorrect for a DataFrame.
# It should be transaction_data['PROD_NAME'].value_counts().head()
print(transaction_data['PROD_NAME'].value_counts().head())

# 2. Text analysis (e.g., word exploration) - The original code was commented out but correct.
# all_prod_words = transaction_data['PROD_NAME'].str.findall(r'\b\w+\b').explode().str.lower()
# word_counts = all_prod_words.value_counts()
# print("\nMost common words in product names (example):")
# print(word_counts.head())

# 3. Remove Salsa products
# The original code was salsa_mask = transaction_data.str.lower().str.contains('salsa', na=False)
# This was trying to apply string methods to the entire DataFrame. It needs to be applied to the 'PROD_NAME' column.
salsa_mask = transaction_data['PROD_NAME'].str.lower().str.contains('salsa', na=False)
print(f"\nNumber of salsa products found: {salsa_mask.sum()}")
transaction_data = transaction_data[~salsa_mask].copy()
print(f"Number of transactions remaining after removing salsa: {len(transaction_data)}")

# C. Summary Statistics and Outlier Management
print("\n--- Initial summary statistics (before PROD_QTY outlier handling) ---")
print(transaction_data.describe(include='all'))

# 2. Investigate `PROD_QTY` outliers
# The original code was outlier_transactions_qty_200 = transaction_data == 200]
# This was attempting to filter the entire DataFrame. It should be based on the 'PROD_QTY' column.
outlier_transactions_qty_200 = transaction_data[transaction_data['PROD_QTY'] == 200]
print("\nTransactions with PROD_QTY = 200:")
print(outlier_transactions_qty_200)

if not outlier_transactions_qty_200.empty:
    # Assume only one customer as in R documentation
    # The original code assumed outlier_customer_id = 226000 directly.
    # It's better to get the customer ID from the filtered data if possible, or keep the assumption explicit.
    # For now, we'll keep the explicit ID as per the R documentation reference.
    outlier_customer_id = 226000 # Based on R documentation
    # The original code was customer_226000_transactions = transaction_data == outlier_customer_id]
    # This was a DataFrame comparison. It should filter based on 'LYLTY_CARD_NBR'.
    customer_226000_transactions = transaction_data[transaction_data['LYLTY_CARD_NBR'] == outlier_customer_id]
    print(f"\nTransactions for customer LYLTY_CARD_NBR = {outlier_customer_id}:")
    print(customer_226000_transactions)

    # 3. Filter out outlier customer
    # The original code was transaction_data = transaction_data!= outlier_customer_id].copy()
    # This was again a DataFrame comparison. It should filter based on 'LYLTY_CARD_NBR'.
    transaction_data = transaction_data[transaction_data['LYLTY_CARD_NBR'] != outlier_customer_id].copy()
    print(f"\nNumber of transactions remaining after removing customer {outlier_customer_id}: {len(transaction_data)}")

print("\n--- Table 1: Summary Statistics of Transaction Data (After Outlier Removal) ---")
# Set datetime_is_numeric=True to include DATE column in statistics if supported by newer pandas versions
try:
    summary_stats_post_outlier = transaction_data.describe(include='all', datetime_is_numeric=True)
except TypeError: # For older pandas versions without datetime_is_numeric
    summary_stats_post_outlier = transaction_data.describe(include='all')
print(summary_stats_post_outlier)

# D. Transaction Trends Over Time
print("\n--- Transaction trends over time ---")
# 1. Count transactions by day
transactions_by_day_counts = transaction_data.groupby('DATE').size().reset_index(name='N')
print(f"Number of days with transactions: {len(transactions_by_day_counts)}")

# 2. Identify and handle missing dates
all_dates_df = pd.DataFrame({'DATE': pd.date_range(start="2018-07-01", end="2019-06-30", freq='D')})
transactions_by_day_full = pd.merge(all_dates_df, transactions_by_day_counts, on='DATE', how='left').fillna({'N': 0})
# The original code was transactions_by_day_full[transactions_by_day_full['N'] == 0] which was missing an index.
missing_transaction_dates = transactions_by_day_full[transactions_by_day_full['N'] == 0]
print("\nDays with no transactions (e.g., Christmas):")
print(missing_transaction_dates)

# 3. Visualize transaction volume
plt.style.use('seaborn-v0_8-whitegrid')

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x='DATE', y='N', data=transactions_by_day_full, ax=ax, color='dodgerblue')
ax.set_title('Number of Transactions Over Time (Overview)', fontsize=16, fontweight='bold')
ax.set_xlabel('Date', fontsize=12)
ax.set_ylabel('Number of Transactions', fontsize=12)
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# The original code was december_transactions = transactions_by_day_full.dt.month == 12] which was incorrect.
# It should access the 'DATE' column's dt accessor.
december_transactions = transactions_by_day_full[transactions_by_day_full['DATE'].dt.month == 12]
fig_dec, ax_dec = plt.subplots(figsize=(12, 6))
sns.lineplot(x='DATE', y='N', data=december_transactions, ax=ax_dec, color='tomato')
ax_dec.set_title('Number of Transactions in December', fontsize=16, fontweight='bold')
ax_dec.set_xlabel('Date', fontsize=12)
ax_dec.set_ylabel('Number of Transactions', fontsize=12)
ax_dec.xaxis.set_major_locator(mdates.DayLocator(interval=2)) # Display every 2 days
ax_dec.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# --- IV. Feature Engineering from Transaction Data ---
print("\n--- Feature Engineering ---")
# A. Extract Pack Size (`PACK_SIZE`)
# Extract the last number in the product name, assuming it's the pack size
# The original code was transaction_data = transaction_data.str.findall(r'\d+').str[-1]
# This was trying to apply string methods to the entire DataFrame. It needs to be applied to 'PROD_NAME'.
transaction_data['PACK_SIZE'] = transaction_data['PROD_NAME'].str.findall(r'\d+').str[-1]
# Handle cases where no number is found (rare with this data)
transaction_data['PACK_SIZE'] = pd.to_numeric(transaction_data['PACK_SIZE'], errors='coerce').fillna(0).astype(int)

print("A few examples of extracted PACK_SIZE:")
# The original code was print(transaction_data].head())
print(transaction_data['PACK_SIZE'].head())

pack_size_counts = transaction_data['PACK_SIZE'].value_counts().sort_index()
print("\nDistribution of PACK_SIZE:")
print(pack_size_counts)

# The original code was transaction_data.hist(bins=len(pack_size_counts) if len(pack_size_counts) < 50 else 50, edgecolor='black')
# This should be on the 'PACK_SIZE' column.
transaction_data['PACK_SIZE'].hist(bins=len(pack_size_counts) if len(pack_size_counts) < 50 else 50, edgecolor='black')
plt.title('Distribution of Pack Size (PACK_SIZE)', fontsize=16, fontweight='bold')
plt.xlabel('Pack Size (g)', fontsize=12)
plt.ylabel('Frequency', fontsize=12)
plt.tight_layout()
plt.show()

# B. Extract and Clean Brand (`BRAND`)
# 1. Extract initial brand (first word)
# The original code was transaction_data = transaction_data.str.split().str.str.upper()
# This was trying to assign a Series back to the DataFrame. It should be assigned to a new column 'BRAND'.
transaction_data['BRAND'] = transaction_data['PROD_NAME'].str.split().str[0].str.upper()

# 2. Standardize brand names
brand_cleaning_map = {
    "RED": "RRD", "SNBTS": "SUNBITES", "INFZNS": "INFUZIONS",
    "WW": "WOOLWORTHS", "SMITH": "SMITHS", "NCC": "NATURAL",
    "DORITO": "DORITOS", "GRAIN": "GRNWVES", # GRNWVES could be Grain Waves
    "CC'S": "CCS" # Added CCS from R data
}
# The original code was transaction_data = transaction_data.replace(brand_cleaning_map)
# This was trying to replace values in the entire DataFrame. It should be applied to the 'BRAND' column.
transaction_data['BRAND'] = transaction_data['BRAND'].replace(brand_cleaning_map)

print("\n--- Table 2: Cleaned Brand Distribution ---")
cleaned_brand_counts = transaction_data['BRAND'].value_counts().sort_index()
print(cleaned_brand_counts.reset_index().rename(columns={'index':'BRAND', 'BRAND':'Count'}))

# --- V. Customer Data: Exploration ---
print("\n--- Exploring Customer Data ---")
# A. Check Structure and Summary
print("Customer data information:")
customer_data.info()
print("\nCustomer data summary statistics:")
print(customer_data.describe(include='all'))

# B. Check Distribution of `LIFESTAGE` and `PREMIUM_CUSTOMER`
print("\nLIFESTAGE distribution:")
# The original code was customer_data.value_counts() which is incorrect for a DataFrame.
# It should be customer_data['LIFESTAGE'].value_counts().
print(customer_data['LIFESTAGE'].value_counts())
print("\nPREMIUM_CUSTOMER distribution:")
# Similarly, for 'PREMIUM_CUSTOMER'.
print(customer_data['PREMIUM_CUSTOMER'].value_counts())

# --- VI. Merge Transaction and Customer Data ---
print("\n--- Merging Data ---")
# A. Perform Merge
merged_data = pd.merge(transaction_data, customer_data, on='LYLTY_CARD_NBR', how='left')
print(f"Number of rows in transaction data: {len(transaction_data)}")
print(f"Number of rows in merged data: {len(merged_data)}")

# B. Verify Integrity
# The original code was null_lifestage_count = merged_data.isnull().sum() and null_premium_customer_count = merged_data.isnull().sum()
# This sums nulls across the entire DataFrame. We need to check specific columns.
null_lifestage_count = merged_data['LIFESTAGE'].isnull().sum()
null_premium_customer_count = merged_data['PREMIUM_CUSTOMER'].isnull().sum()
print(f"Number of null values in LIFESTAGE after merge: {null_lifestage_count}")
print(f"Number of null values in PREMIUM_CUSTOMER after merge: {null_premium_customer_count}")

if null_lifestage_count == 0 and null_premium_customer_count == 0:
    print("Merge successful, no transactions missing customer information.")
else:
    print("Warning: Some transactions are missing customer information after merge.")

# C. (Optional) Save Merged Data
# merged_data.to_csv("QVI_data_python.csv", index=False)
# print(f"\nMerged data can be saved at: QVI_data_python.csv")


# --- VII. Customer Segmentation Analysis ---
print("\n--- Customer Segmentation Analysis ---")

# A. Total Sales by `LIFESTAGE` and `PREMIUM_CUSTOMER`
# The original code was merged_data.groupby(, observed=True).sum().reset_index(name='SALES')
# Missing the columns to group by.
sales_by_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True)['TOT_SALES'].sum().reset_index(name='SALES')
print("\n--- Table 3: Total Sales by LIFESTAGE and PREMIUM_CUSTOMER (Top 10) ---")
print(sales_by_segment.sort_values(by='SALES', ascending=False).head(10))

sales_pivot = sales_by_segment.pivot_table(index='PREMIUM_CUSTOMER', columns='LIFESTAGE', values='SALES')
plt.figure(figsize=(14, 8))
sns.heatmap(sales_pivot, annot=True, fmt=".0f", cmap="viridis", linewidths=.5,
            cbar_kws={'label': 'Total Sales ($)'})
plt.title('Total Sales by LIFESTAGE and PREMIUM_CUSTOMER', fontsize=16, fontweight='bold')
plt.ylabel('Premium Customer Segment', fontsize=12)
plt.xlabel('Lifestage', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# B. Number of Customers by `LIFESTAGE` and `PREMIUM_CUSTOMER`
# The original code was merged_data.groupby(, observed=True).nunique().reset_index(name='CUSTOMERS')
# Missing the columns to group by and the column for nunique().
num_customers_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True)['LYLTY_CARD_NBR'].nunique().reset_index(name='CUSTOMERS')
print("\n--- Table 4: Number of Customers by LIFESTAGE and PREMIUM_CUSTOMER (Top 10) ---")
print(num_customers_segment.sort_values(by='CUSTOMERS', ascending=False).head(10))

customers_pivot = num_customers_segment.pivot_table(index='PREMIUM_CUSTOMER', columns='LIFESTAGE', values='CUSTOMERS')
plt.figure(figsize=(14, 8))
sns.heatmap(customers_pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=.5,
            cbar_kws={'label': 'Number of Customers'})
plt.title('Number of Customers by LIFESTAGE and PREMIUM_CUSTOMER', fontsize=16, fontweight='bold')
plt.ylabel('Premium Customer Segment', fontsize=12)
plt.xlabel('Lifestage', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# C. Average Units per Customer by Segment
# The original code was merged_data.groupby(, observed=True).agg(...)
# Missing the columns to group by.
avg_units_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True).agg(
    total_qty=('PROD_QTY', 'sum'),
    unique_customers=('LYLTY_CARD_NBR', 'nunique')
).reset_index()
# The original code was avg_units_segment = avg_units_segment['total_qty'] / avg_units_segment['unique_customers']
# This assigns directly to the variable, losing the DataFrame structure needed for plotting.
# We need to add a new column for this.
avg_units_segment['AVG_UNITS_PER_CUSTOMER'] = avg_units_segment['total_qty'] / avg_units_segment['unique_customers']
print("\n--- Table 5: Average Units per Customer by Segment (Top 10) ---")
print(avg_units_segment.sort_values(by='AVG_UNITS_PER_CUSTOMER', ascending=False).head(10))

plt.figure(figsize=(12, 7))
sns.barplot(x='LIFESTAGE', y='AVG_UNITS_PER_CUSTOMER', hue='PREMIUM_CUSTOMER', data=avg_units_segment, palette='viridis', dodge=True)
plt.title('Average Units per Customer by Segment', fontsize=16, fontweight='bold')
plt.xlabel('Lifestage', fontsize=12)
plt.ylabel('Avg. Units / Customer', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Customer Segment')
plt.tight_layout()
plt.show()

# D. Average Price per Unit by Segment
# The original code was merged_data.groupby(, observed=True).agg(...)
# Missing the columns to group by.
avg_price_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True).agg(
    total_sales_val=('TOT_SALES', 'sum'),
    total_qty_val=('PROD_QTY', 'sum')
).reset_index()
# The original code was avg_price_segment = avg_price_segment['total_sales_val'] / avg_price_segment['total_qty_val']
# Similar to above, assign to a new column.
avg_price_segment['AVG_PRICE_PER_UNIT'] = avg_price_segment['total_sales_val'] / avg_price_segment['total_qty_val']
print("\n--- Table 6: Average Price per Unit by Segment (Top 10) ---")
print(avg_price_segment.sort_values(by='AVG_PRICE_PER_UNIT', ascending=False).head(10))

plt.figure(figsize=(12, 7))
sns.barplot(x='LIFESTAGE', y='AVG_PRICE_PER_UNIT', hue='PREMIUM_CUSTOMER', data=avg_price_segment, palette='coolwarm', dodge=True)
plt.title('Average Price per Unit by Segment', fontsize=16, fontweight='bold')
plt.xlabel('Lifestage', fontsize=12)
plt.ylabel('Avg. Price / Unit ($)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Customer Segment')
plt.tight_layout()
plt.show()

# E. Statistical Significance Test (T-test)
# The original code was merged_data = merged_data / merged_data which is a nonsensical operation.
# It should be filtering the 'AVG_PRICE_PER_UNIT' values from the merged_data based on LIFESTAGE and PREMIUM_CUSTOMER.
# We need to calculate the average price per unit for each transaction first or filter the already calculated average prices.
# Let's recalculate price per unit at transaction level.
merged_data['PRICE_PER_UNIT'] = merged_data['TOT_SALES'] / merged_data['PROD_QTY']

# Correcting group definitions for the t-test
group_mainstream = merged_data[
    (merged_data['LIFESTAGE'].isin(["YOUNG SINGLES/COUPLES", "MIDAGE SINGLES/COUPLES"])) &
    (merged_data['PREMIUM_CUSTOMER'] == "Mainstream")
]['PRICE_PER_UNIT'].dropna()

group_other = merged_data[
    (merged_data['LIFESTAGE'].isin(["YOUNG SINGLES/COUPLES", "MIDAGE SINGLES/COUPLES"])) &
    (merged_data['PREMIUM_CUSTOMER'].isin(["Budget", "Premium"])) # Includes Budget and Premium
]['PRICE_PER_UNIT'].dropna()

if not group_mainstream.empty and not group_other.empty:
    t_stat, p_value = stats.ttest_ind(group_mainstream, group_other,
                                      equal_var=False, # Welch's t-test
                                      alternative='greater') # Test if mainstream is greater
    print("\n--- Table 7: T-test Results for Price Per Unit ---")
    print(f"Comparison: Mainstream (Young/Midage Singles/Couples) vs. Budget/Premium (Young/Midage Singles/Couples)")
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}") # Formatting p-value for readability
    print(f"Avg Price (Mainstream): {group_mainstream.mean():.4f}")
    print(f"Avg Price (Budget/Premium): {group_other.mean():.4f}")
    if p_value < 0.05:
        print("Conclusion: There is statistical evidence that the Mainstream group pays a significantly higher price per unit.")
    else:
        print("Conclusion: There is not enough statistical evidence that the Mainstream group pays a significantly higher price per unit.")
else:
    print("\nNot enough data to perform T-test for the selected groups.")


# --- VIII. Deep Dive: 'Mainstream, Young Singles/Couples' Segment ---
print("\n--- Deep Dive: Mainstream, Young Singles/Couples ---")
target_lifestage = "YOUNG SINGLES/COUPLES"
target_premium = "Mainstream"

# Filtering segments correctly
segment1 = merged_data[
    (merged_data['LIFESTAGE'] == target_lifestage) &
    (merged_data['PREMIUM_CUSTOMER'] == target_premium)
].copy()

# The 'other_segments' should include all other customers, not just those in the same lifestage but different premium.
# For comparing to the *rest* of the market, it's typically all data excluding the target segment.
# If the intention was to compare against *other* premium customers within the same lifestage, the original logic was closer.
# Let's assume 'other' means *all other customers* for a broader comparison, consistent with typical market analysis.
other_segments = merged_data[
    ~((merged_data['LIFESTAGE'] == target_lifestage) &
      (merged_data['PREMIUM_CUSTOMER'] == target_premium))
].copy()

if not segment1.empty and not other_segments.empty:
    # A. Brand Preference Analysis
    # The original code was quantity_segment1_total = segment1.sum()
    # This sums all numeric columns. We need 'PROD_QTY' specifically.
    quantity_segment1_total = segment1['PROD_QTY'].sum()
    quantity_other_total = other_segments['PROD_QTY'].sum()

    quantity_segment1_by_brand = segment1.groupby('BRAND', observed=True)['PROD_QTY'].sum() / quantity_segment1_total
    quantity_other_by_brand = other_segments.groupby('BRAND', observed=True)['PROD_QTY'].sum() / quantity_other_total

    brand_affinity = pd.merge(
        quantity_segment1_by_brand.rename('targetSegment'),
        quantity_other_by_brand.rename('other'),
        on='BRAND', how='outer'
    ).fillna(0)
    # Correcting the affinity calculation: affinity is target_share / other_share
    brand_affinity['affinityToBrand'] = brand_affinity['targetSegment'] / brand_affinity['other']
    brand_affinity.replace([float('inf'), -float('inf')], pd.NA, inplace=True) # Handle division by zero
    brand_affinity.dropna(subset=['affinityToBrand'], inplace=True) # Remove NA due to division by zero

    print("\n--- Table 8: Brand Affinity of 'Mainstream, Young Singles/Couples' Segment (Top 10) ---")
    print(brand_affinity.sort_values(by='affinityToBrand', ascending=False).head(10))

    # B. Pack Size Preference Analysis
    quantity_segment1_by_pack = segment1.groupby('PACK_SIZE')['PROD_QTY'].sum() / quantity_segment1_total
    quantity_other_by_pack = other_segments.groupby('PACK_SIZE')['PROD_QTY'].sum() / quantity_other_total

    pack_affinity = pd.merge(
        quantity_segment1_by_pack.rename('targetSegment'),
        quantity_other_by_pack.rename('other'),
        on='PACK_SIZE', how='outer'
    ).fillna(0)
    # Correcting the affinity calculation
    pack_affinity['affinityToPack'] = pack_affinity['targetSegment'] / pack_affinity['other']
    pack_affinity.replace([float('inf'), -float('inf')], pd.NA, inplace=True)
    pack_affinity.dropna(subset=['affinityToPack'], inplace=True)

    print("\n--- Table 9: Pack Size Preference of 'Mainstream, Young Singles/Couples' Segment (Top 10) ---")
    print(pack_affinity.sort_values(by='affinityToPack', ascending=False).head(10))

    # Investigate brands for high affinity pack size (e.g., 270g from R results)
    high_affinity_pack_size = 270 # Based on results from R documentation
    # The original code was merged_data == high_affinity_pack_size].unique() which is incorrect syntax.
    # It should filter merged_data based on 'PACK_SIZE' and then get unique brands.
    if high_affinity_pack_size in pack_affinity.index: # Check if pack size exists in the affinity results
        brands_for_pack_size_270 = merged_data[merged_data['PACK_SIZE'] == high_affinity_pack_size]['BRAND'].unique()
        print(f"\nProducts with {high_affinity_pack_size}g pack size: {', '.join(brands_for_pack_size_270)}")
    else:
        # Fallback if 270g is not the top, pick the actual top from calculation
        if not pack_affinity.empty:
            top_pack_size_from_py = pack_affinity.sort_values(by='affinityToPack', ascending=False).index[0]
            brands_for_top_pack_size = merged_data[merged_data['PACK_SIZE'] == top_pack_size_from_py]['BRAND'].unique()
            print(f"\nProducts with highest affinity pack size ({top_pack_size_from_py}g): {', '.join(brands_for_top_pack_size)}")

else:
    print("\nNot enough data in segment1 or other_segments to perform deep dive analysis.")


# --- IX. Conclusion and Analysis Summary ---
# This section is primarily text, to be presented in the main report.
print("\n--- Analysis complete. Please refer to the report for detailed conclusions. ---")