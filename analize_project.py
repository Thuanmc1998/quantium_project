import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import re # For more complex string operations if needed
# --- II.   Thiết Lập Môi Trường Python và Tải Dữ Liệu ---

# B. Tải Dữ Liệu
# Giả định các tệp CSV nằm trong cùng thư mục với kịch bản

transaction_data_raw = pd.ExcelFile("QVI_transaction_data.xlsx")
customer_data = pd.read_csv('QVI_purchase_behaviour.csv')

# Tạo bản sao để thao tác, giữ nguyên dữ liệu gốc
transaction_data = transaction_data_raw.parse('in')

print("--- Thông tin ban đầu của dữ liệu giao dịch ---")
transaction_data.info()
print("\n--- 5 dòng đầu của dữ liệu giao dịch ---")
print(transaction_data.head())

print("\n--- Thông tin ban đầu của dữ liệu khách hàng ---")
customer_data.info()
print("\n--- 5 dòng đầu của dữ liệu khách hàng ---")
print(customer_data.head())

# --- III. Dữ Liệu Giao Dịch: Tiền Xử Lý và Phân Tích Thăm Dò ---

# A. Chuyển Đổi Cột Ngày (DATE)
print("\n--- Chuyển đổi cột DATE ---")
# The original code had transaction_data = pd.to_datetime(transaction_data, origin='1899-12-30', unit='D')
# This attempts to convert the entire DataFrame. We need to specify the 'DATE' column.
transaction_data['DATE'] = pd.to_datetime(transaction_data['DATE'], origin='1899-12-30', unit='D')
print(f"Kiểu dữ liệu cột DATE sau chuyển đổi: {transaction_data['DATE'].dtype}")
print(transaction_data['DATE'].head()) # Accessing the 'DATE' column for head()

# B. Phân Tích Cột Tên Sản Phẩm (`PROD_NAME`)
print("\n--- Phân tích PROD_NAME ---")
# 1. Kiểm tra các tên sản phẩm duy nhất (ví dụ)
print("Một số tên sản phẩm và số lượng:")
# The original code was transaction_data.value_counts().head() which is incorrect for a DataFrame.
# It should be transaction_data['PROD_NAME'].value_counts().head()
print(transaction_data['PROD_NAME'].value_counts().head())

# 2. Phân tích văn bản (ví dụ khám phá từ) - The original code was commented out but correct.
# all_prod_words = transaction_data['PROD_NAME'].str.findall(r'\b\w+\b').explode().str.lower()
# word_counts = all_prod_words.value_counts()
# print("\nCác từ phổ biến nhất trong tên sản phẩm (ví dụ):")
# print(word_counts.head())

# 3. Loại bỏ sản phẩm Salsa
# The original code was salsa_mask = transaction_data.str.lower().str.contains('salsa', na=False)
# This was trying to apply string methods to the entire DataFrame. It needs to be applied to the 'PROD_NAME' column.
salsa_mask = transaction_data['PROD_NAME'].str.lower().str.contains('salsa', na=False)
print(f"\nSố lượng sản phẩm salsa tìm thấy: {salsa_mask.sum()}")
transaction_data = transaction_data[~salsa_mask].copy()
print(f"Số lượng giao dịch còn lại sau khi loại bỏ salsa: {len(transaction_data)}")

# C. Thống Kê Tóm Tắt và Quản Lý Ngoại Lệ
print("\n--- Thống kê tóm tắt ban đầu (trước khi xử lý ngoại lệ PROD_QTY) ---")
print(transaction_data.describe(include='all'))

# 2. Điều tra ngoại lệ `PROD_QTY`
# The original code was outlier_transactions_qty_200 = transaction_data == 200]
# This was attempting to filter the entire DataFrame. It should be based on the 'PROD_QTY' column.
outlier_transactions_qty_200 = transaction_data[transaction_data['PROD_QTY'] == 200]
print("\nCác giao dịch có PROD_QTY = 200:")
print(outlier_transactions_qty_200)

if not outlier_transactions_qty_200.empty:
    # Giả sử chỉ có một khách hàng như trong tài liệu R
    # The original code assumed outlier_customer_id = 226000 directly.
    # It's better to get the customer ID from the filtered data if possible, or keep the assumption explicit.
    # For now, we'll keep the explicit ID as per the R documentation reference.
    outlier_customer_id = 226000 # Dựa trên tài liệu R
    # The original code was customer_226000_transactions = transaction_data == outlier_customer_id]
    # This was a DataFrame comparison. It should filter based on 'LYLTY_CARD_NBR'.
    customer_226000_transactions = transaction_data[transaction_data['LYLTY_CARD_NBR'] == outlier_customer_id]
    print(f"\nCác giao dịch của khách hàng LYLTY_CARD_NBR = {outlier_customer_id}:")
    print(customer_226000_transactions)

    # 3. Lọc bỏ khách hàng ngoại lệ
    # The original code was transaction_data = transaction_data!= outlier_customer_id].copy()
    # This was again a DataFrame comparison. It should filter based on 'LYLTY_CARD_NBR'.
    transaction_data = transaction_data[transaction_data['LYLTY_CARD_NBR'] != outlier_customer_id].copy()
    print(f"\nSố lượng giao dịch còn lại sau khi loại bỏ khách hàng {outlier_customer_id}: {len(transaction_data)}")

print("\n--- Bảng 1: Thống Kê Tóm Tắt Dữ Liệu Giao Dịch (Sau Khi Loại Bỏ Ngoại Lệ) ---")
# Đặt datetime_is_numeric=True để bao gồm cột DATE trong thống kê nếu pandas phiên bản mới hỗ trợ
try:
    summary_stats_post_outlier = transaction_data.describe(include='all', datetime_is_numeric=True)
except TypeError: # Dành cho pandas phiên bản cũ hơn không có datetime_is_numeric
    summary_stats_post_outlier = transaction_data.describe(include='all')
print(summary_stats_post_outlier)

# D. Xu Hướng Giao Dịch Theo Thời Gian
print("\n--- Xu hướng giao dịch theo thời gian ---")
# 1. Đếm số giao dịch theo ngày
transactions_by_day_counts = transaction_data.groupby('DATE').size().reset_index(name='N')
print(f"Số ngày có giao dịch: {len(transactions_by_day_counts)}")

# 2. Xác định và xử lý ngày bị thiếu
all_dates_df = pd.DataFrame({'DATE': pd.date_range(start="2018-07-01", end="2019-06-30", freq='D')})
transactions_by_day_full = pd.merge(all_dates_df, transactions_by_day_counts, on='DATE', how='left').fillna({'N': 0})
# The original code was transactions_by_day_full[transactions_by_day_full['N'] == 0] which was missing an index.
missing_transaction_dates = transactions_by_day_full[transactions_by_day_full['N'] == 0]
print("\nNgày không có giao dịch (ví dụ: Giáng Sinh):")
print(missing_transaction_dates)

# 3. Trực quan hóa khối lượng giao dịch
plt.style.use('seaborn-v0_8-whitegrid')

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x='DATE', y='N', data=transactions_by_day_full, ax=ax, color='dodgerblue')
ax.set_title('Số Lượng Giao Dịch Theo Thời Gian (Tổng Quan)', fontsize=16, fontweight='bold')
ax.set_xlabel('Ngày', fontsize=12)
ax.set_ylabel('Số Lượng Giao Dịch', fontsize=12)
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
ax_dec.set_title('Số Lượng Giao Dịch Tháng 12', fontsize=16, fontweight='bold')
ax_dec.set_xlabel('Ngày', fontsize=12)
ax_dec.set_ylabel('Số Lượng Giao Dịch', fontsize=12)
ax_dec.xaxis.set_major_locator(mdates.DayLocator(interval=2)) # Hiển thị mỗi 2 ngày
ax_dec.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()

# --- IV. Kỹ Thuật Tạo Đặc Trưng từ Dữ Liệu Giao Dịch ---
print("\n--- Kỹ thuật tạo đặc trưng ---")
# A. Trích Xuất Kích Thước Gói (`PACK_SIZE`)
# Trích xuất số cuối cùng trong tên sản phẩm, giả định đó là kích thước gói
# The original code was transaction_data = transaction_data.str.findall(r'\d+').str[-1]
# This was trying to apply string methods to the entire DataFrame. It needs to be applied to 'PROD_NAME'.
transaction_data['PACK_SIZE'] = transaction_data['PROD_NAME'].str.findall(r'\d+').str[-1]
# Xử lý trường hợp không tìm thấy số (hiếm khi xảy ra với dữ liệu này)
transaction_data['PACK_SIZE'] = pd.to_numeric(transaction_data['PACK_SIZE'], errors='coerce').fillna(0).astype(int)

print("Một vài ví dụ về PACK_SIZE được trích xuất:")
# The original code was print(transaction_data].head())
print(transaction_data['PACK_SIZE'].head())

pack_size_counts = transaction_data['PACK_SIZE'].value_counts().sort_index()
print("\nPhân phối PACK_SIZE:")
print(pack_size_counts)

# The original code was transaction_data.hist(bins=len(pack_size_counts) if len(pack_size_counts) < 50 else 50, edgecolor='black')
# This should be on the 'PACK_SIZE' column.
transaction_data['PACK_SIZE'].hist(bins=len(pack_size_counts) if len(pack_size_counts) < 50 else 50, edgecolor='black')
plt.title('Phân Phối Kích Thước Gói (PACK_SIZE)', fontsize=16, fontweight='bold')
plt.xlabel('Kích Thước Gói (g)', fontsize=12)
plt.ylabel('Tần Suất', fontsize=12)
plt.tight_layout()
plt.show()

# B. Trích Xuất và Làm Sạch Thương Hiệu (`BRAND`)
# 1. Trích xuất thương hiệu ban đầu (từ đầu tiên)
# The original code was transaction_data = transaction_data.str.split().str.str.upper()
# This was trying to assign a Series back to the DataFrame. It should be assigned to a new column 'BRAND'.
transaction_data['BRAND'] = transaction_data['PROD_NAME'].str.split().str[0].str.upper()

# 2. Chuẩn hóa tên thương hiệu
brand_cleaning_map = {
    "RED": "RRD", "SNBTS": "SUNBITES", "INFZNS": "INFUZIONS",
    "WW": "WOOLWORTHS", "SMITH": "SMITHS", "NCC": "NATURAL",
    "DORITO": "DORITOS", "GRAIN": "GRNWVES", # GRNWVES có thể là Grain Waves
    "CC'S": "CCS" # Thêm CCS từ dữ liệu R
}
# The original code was transaction_data = transaction_data.replace(brand_cleaning_map)
# This was trying to replace values in the entire DataFrame. It should be applied to the 'BRAND' column.
transaction_data['BRAND'] = transaction_data['BRAND'].replace(brand_cleaning_map)

print("\n--- Bảng 2: Phân Phối Thương Hiệu Đã Được Làm Sạch ---")
cleaned_brand_counts = transaction_data['BRAND'].value_counts().sort_index()
print(cleaned_brand_counts.reset_index().rename(columns={'index':'BRAND', 'BRAND':'Count'}))

# --- V. Dữ Liệu Khách Hàng: Thăm Dò ---
print("\n--- Thăm dò dữ liệu khách hàng ---")
# A. Kiểm Tra Cấu Trúc và Tóm Tắt
print("Thông tin dữ liệu khách hàng:")
customer_data.info()
print("\nThống kê tóm tắt dữ liệu khách hàng:")
print(customer_data.describe(include='all'))

# B. Kiểm Tra Phân Phối `LIFESTAGE` và `PREMIUM_CUSTOMER`
print("\nPhân phối LIFESTAGE:")
# The original code was customer_data.value_counts() which is incorrect for a DataFrame.
# It should be customer_data['LIFESTAGE'].value_counts().
print(customer_data['LIFESTAGE'].value_counts())
print("\nPhân phối PREMIUM_CUSTOMER:")
# Similarly, for 'PREMIUM_CUSTOMER'.
print(customer_data['PREMIUM_CUSTOMER'].value_counts())

# --- VI. Hợp Nhất Dữ Liệu Giao Dịch và Khách Hàng ---
print("\n--- Hợp nhất dữ liệu ---")
# A. Thực Hiện Hợp Nhất
merged_data = pd.merge(transaction_data, customer_data, on='LYLTY_CARD_NBR', how='left')
print(f"Số hàng trong dữ liệu giao dịch: {len(transaction_data)}")
print(f"Số hàng trong dữ liệu đã hợp nhất: {len(merged_data)}")

# B. Xác Minh Tính Toàn Vẹn
# The original code was null_lifestage_count = merged_data.isnull().sum() and null_premium_customer_count = merged_data.isnull().sum()
# This sums nulls across the entire DataFrame. We need to check specific columns.
null_lifestage_count = merged_data['LIFESTAGE'].isnull().sum()
null_premium_customer_count = merged_data['PREMIUM_CUSTOMER'].isnull().sum()
print(f"Số giá trị null trong LIFESTAGE sau khi hợp nhất: {null_lifestage_count}")
print(f"Số giá trị null trong PREMIUM_CUSTOMER sau khi hợp nhất: {null_premium_customer_count}")

if null_lifestage_count == 0 and null_premium_customer_count == 0:
    print("Hợp nhất thành công, không có giao dịch nào thiếu thông tin khách hàng.")
else:
    print("Cảnh báo: Có giao dịch thiếu thông tin khách hàng sau khi hợp nhất.")

# C. (Tùy chọn) Lưu Dữ Liệu Đã Hợp Nhất
# merged_data.to_csv("QVI_data_python.csv", index=False)
# print(f"\nDữ liệu đã hợp nhất có thể được lưu tại: QVI_data_python.csv")


# --- VII. Phân Tích Phân Khúc Khách Hàng ---
print("\n--- Phân tích phân khúc khách hàng ---")

# A. Tổng Doanh Số theo `LIFESTAGE` và `PREMIUM_CUSTOMER`
# The original code was merged_data.groupby(, observed=True).sum().reset_index(name='SALES')
# Missing the columns to group by.
sales_by_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True)['TOT_SALES'].sum().reset_index(name='SALES')
print("\n--- Bảng 3: Tổng Doanh Số theo LIFESTAGE và PREMIUM_CUSTOMER (Top 10) ---")
print(sales_by_segment.sort_values(by='SALES', ascending=False).head(10))

sales_pivot = sales_by_segment.pivot_table(index='PREMIUM_CUSTOMER', columns='LIFESTAGE', values='SALES')
plt.figure(figsize=(14, 8))
sns.heatmap(sales_pivot, annot=True, fmt=".0f", cmap="viridis", linewidths=.5,
            cbar_kws={'label': 'Tổng Doanh Số ($)'})
plt.title('Tổng Doanh Số theo LIFESTAGE và PREMIUM_CUSTOMER', fontsize=16, fontweight='bold')
plt.ylabel('Phân Khúc Khách Hàng', fontsize=12)
plt.xlabel('Giai Đoạn Sống', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# B. Số Lượng Khách Hàng theo `LIFESTAGE` và `PREMIUM_CUSTOMER`
# The original code was merged_data.groupby(, observed=True).nunique().reset_index(name='CUSTOMERS')
# Missing the columns to group by and the column for nunique().
num_customers_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True)['LYLTY_CARD_NBR'].nunique().reset_index(name='CUSTOMERS')
print("\n--- Bảng 4: Số Lượng Khách Hàng theo LIFESTAGE và PREMIUM_CUSTOMER (Top 10) ---")
print(num_customers_segment.sort_values(by='CUSTOMERS', ascending=False).head(10))

customers_pivot = num_customers_segment.pivot_table(index='PREMIUM_CUSTOMER', columns='LIFESTAGE', values='CUSTOMERS')
plt.figure(figsize=(14, 8))
sns.heatmap(customers_pivot, annot=True, fmt=".0f", cmap="YlGnBu", linewidths=.5,
            cbar_kws={'label': 'Số Lượng Khách Hàng'})
plt.title('Số Lượng Khách Hàng theo LIFESTAGE và PREMIUM_CUSTOMER', fontsize=16, fontweight='bold')
plt.ylabel('Phân Khúc Khách Hàng', fontsize=12)
plt.xlabel('Giai Đoạn Sống', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
plt.show()

# C. Số Lượng Đơn Vị Trung Bình trên Mỗi Khách Hàng theo Phân Khúc
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
print("\n--- Bảng 5: Số Lượng Đơn Vị Trung Bình trên Mỗi Khách Hàng theo Phân Khúc (Top 10) ---")
print(avg_units_segment.sort_values(by='AVG_UNITS_PER_CUSTOMER', ascending=False).head(10))

plt.figure(figsize=(12, 7))
sns.barplot(x='LIFESTAGE', y='AVG_UNITS_PER_CUSTOMER', hue='PREMIUM_CUSTOMER', data=avg_units_segment, palette='viridis', dodge=True)
plt.title('Số Lượng Đơn Vị Trung Bình trên Mỗi Khách Hàng theo Phân Khúc', fontsize=16, fontweight='bold')
plt.xlabel('Giai Đoạn Sống', fontsize=12)
plt.ylabel('Số Lượng Đơn Vị TB / Khách Hàng', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Phân Khúc KH')
plt.tight_layout()
plt.show()

# D. Giá Trung Bình trên Mỗi Đơn Vị theo Phân Khúc
# The original code was merged_data.groupby(, observed=True).agg(...)
# Missing the columns to group by.
avg_price_segment = merged_data.groupby(['LIFESTAGE', 'PREMIUM_CUSTOMER'], observed=True).agg(
    total_sales_val=('TOT_SALES', 'sum'),
    total_qty_val=('PROD_QTY', 'sum')
).reset_index()
# The original code was avg_price_segment = avg_price_segment['total_sales_val'] / avg_price_segment['total_qty_val']
# Similar to above, assign to a new column.
avg_price_segment['AVG_PRICE_PER_UNIT'] = avg_price_segment['total_sales_val'] / avg_price_segment['total_qty_val']
print("\n--- Bảng 6: Giá Trung Bình trên Mỗi Đơn Vị theo Phân Khúc (Top 10) ---")
print(avg_price_segment.sort_values(by='AVG_PRICE_PER_UNIT', ascending=False).head(10))

plt.figure(figsize=(12, 7))
sns.barplot(x='LIFESTAGE', y='AVG_PRICE_PER_UNIT', hue='PREMIUM_CUSTOMER', data=avg_price_segment, palette='coolwarm', dodge=True)
plt.title('Giá Trung Bình trên Mỗi Đơn Vị theo Phân Khúc', fontsize=16, fontweight='bold')
plt.xlabel('Giai Đoạn Sống', fontsize=12)
plt.ylabel('Giá TB / Đơn Vị ($)', fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.legend(title='Phân Khúc KH')
plt.tight_layout()
plt.show()

# E. Kiểm Định Ý Nghĩa Thống Kê (T-test)
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
    print("\n--- Bảng 7: Kết Quả T-test cho Giá Mỗi Đơn Vị ---")
    print(f"So sánh: Mainstream (Young/Midage Singles/Couples) vs. Budget/Premium (Young/Midage Singles/Couples)")
    print(f"T-statistic: {t_stat:.4f}")
    print(f"P-value: {p_value:.4f}") # Formatting p-value for readability
    print(f"Giá TB (Mainstream): {group_mainstream.mean():.4f}")
    print(f"Giá TB (Budget/Premium): {group_other.mean():.4f}")
    if p_value < 0.05:
        print("Kết luận: Có bằng chứng thống kê cho thấy nhóm Mainstream trả giá mỗi đơn vị cao hơn đáng kể.")
    else:
        print("Kết luận: Không có đủ bằng chứng thống kê cho thấy nhóm Mainstream trả giá mỗi đơn vị cao hơn đáng kể.")
else:
    print("\nKhông đủ dữ liệu để thực hiện T-test cho các nhóm đã chọn.")


# --- VIII. Phân Tích Sâu: Phân Khúc 'Mainstream, Young Singles/Couples' ---
print("\n--- Phân tích sâu: Mainstream, Young Singles/Couples ---")
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
    # A. Phân Tích Mức Độ Ưa Thích Thương Hiệu
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
    brand_affinity.replace([float('inf'), -float('inf')], pd.NA, inplace=True) # Xử lý chia cho 0
    brand_affinity.dropna(subset=['affinityToBrand'], inplace=True) # Loại bỏ NA do chia cho 0

    print("\n--- Bảng 8: Mức Độ Ưa Thích Thương Hiệu của Phân Khúc 'Mainstream, Young Singles/Couples' (Top 10) ---")
    print(brand_affinity.sort_values(by='affinityToBrand', ascending=False).head(10))

    # B. Phân Tích Sở Thích Kích Thước Gói
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

    print("\n--- Bảng 9: Sở Thích Kích Thước Gói của Phân Khúc 'Mainstream, Young Singles/Couples' (Top 10) ---")
    print(pack_affinity.sort_values(by='affinityToPack', ascending=False).head(10))

    # Điều tra các thương hiệu cho kích thước gói có mức độ ưa thích cao (ví dụ: 270g từ kết quả R)
    high_affinity_pack_size = 270 # Dựa trên kết quả từ tài liệu R
    # The original code was merged_data == high_affinity_pack_size].unique() which is incorrect syntax.
    # It should filter merged_data based on 'PACK_SIZE' and then get unique brands.
    if high_affinity_pack_size in pack_affinity.index: # Check if pack size exists in the affinity results
        brands_for_pack_size_270 = merged_data[merged_data['PACK_SIZE'] == high_affinity_pack_size]['BRAND'].unique()
        print(f"\nCác sản phẩm có kích thước gói {high_affinity_pack_size}g: {', '.join(brands_for_pack_size_270)}")
    else:
        # Fallback if 270g is not the top, pick the actual top from calculation
        if not pack_affinity.empty:
            top_pack_size_from_py = pack_affinity.sort_values(by='affinityToPack', ascending=False).index[0]
            brands_for_top_pack_size = merged_data[merged_data['PACK_SIZE'] == top_pack_size_from_py]['BRAND'].unique()
            print(f"\nCác sản phẩm có kích thước gói ưa thích nhất ({top_pack_size_from_py}g): {', '.join(brands_for_top_pack_size)}")

else:
    print("\nKhông đủ dữ liệu trong segment1 hoặc other_segments để thực hiện phân tích sâu.")


# --- IX. Kết Luận và Tóm Tắt Phân Tích ---
# Phần này chủ yếu là văn bản, được trình bày trong báo cáo chính.
print("\n--- Phân tích hoàn tất. Vui lòng xem báo cáo để biết kết luận chi tiết. ---")