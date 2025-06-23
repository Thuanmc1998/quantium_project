VIETNAMESE VER. (ENGLISH VER. BELOW)
# Phân Tích Dữ Liệu Giao Dịch và Hành Vi Khách Hàng QVI

## Giới Thiệu

Dự án này là một phân tích dữ liệu chuyên sâu về hành vi mua sắm của khách hàng và dữ liệu giao dịch từ QVI (Quantium Virtual Internship). Mục tiêu chính là khám phá các mô hình tiêu dùng, phân khúc khách hàng dựa trên giai đoạn sống (`LIFESTAGE`) và loại khách hàng (`PREMIUM_CUSTOMER`), từ đó đưa ra các khuyến nghị kinh doanh.

Dự án thực hiện các bước từ tiền xử lý dữ liệu thô, làm sạch, kỹ thuật tạo đặc trưng đến phân tích thăm dò và hợp nhất dữ liệu, cuối cùng là phân tích chuyên sâu các phân khúc khách hàng tiềm năng.

## Bộ Dữ Liệu

Dự án sử dụng hai bộ dữ liệu chính:

1.  **`QVI_transaction_data.xlsx`**: Chứa thông tin chi tiết về các giao dịch mua hàng, bao gồm ngày giao dịch, tên sản phẩm, số lượng và tổng doanh số.
2.  **`QVI_purchase_behaviour.csv`**: Chứa thông tin về hành vi mua sắm của khách hàng, bao gồm `LIFESTAGE` và `PREMIUM_CUSTOMER` cho mỗi số thẻ khách hàng thân thiết.

## Các Bước Phân Tích Chính

Dự án được cấu trúc thành các phần chính sau:

### I. Thiết Lập Môi Trường Python và Tải Dữ Liệu

* Import các thư viện cần thiết: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy.stats`, `re`.
* Tải dữ liệu giao dịch và dữ liệu khách hàng vào các DataFrame.

### II. Dữ Liệu Giao Dịch: Tiền Xử Lý và Phân Tích Thăm Dò

* **Chuyển đổi cột `DATE`**: Chuyển đổi định dạng ngày từ số nguyên sang định dạng ngày tháng chuẩn.
* **Phân tích `PROD_NAME`**:
    * Khám phá các tên sản phẩm duy nhất.
    * Loại bỏ các sản phẩm không liên quan (ví dụ: "Salsa").
* **Thống kê Tóm tắt & Quản lý Ngoại lệ**:
    * Kiểm tra thống kê mô tả ban đầu.
    * Xác định và xử lý các giao dịch ngoại lệ (ví dụ: `PROD_QTY` = 200).
    * Loại bỏ các khách hàng có hành vi mua hàng bất thường.
* **Xu hướng Giao dịch Theo Thời Gian**:
    * Đếm số lượng giao dịch theo ngày.
    * Xác định các ngày thiếu dữ liệu (ví dụ: Giáng Sinh).
    * Trực quan hóa khối lượng giao dịch để nhận diện xu hướng theo thời gian.

### III. Kỹ Thuật Tạo Đặc Trưng từ Dữ Liệu Giao Dịch

* **Trích xuất `PACK_SIZE`**: Trích xuất kích thước gói sản phẩm từ tên sản phẩm để phân tích sở thích về kích thước.
* **Trích xuất và Làm sạch `BRAND`**: Trích xuất tên thương hiệu từ tên sản phẩm và chuẩn hóa chúng để phân tích nhất quán.

### IV. Dữ Liệu Khách Hàng: Thăm Dò

* Kiểm tra cấu trúc và thống kê tóm tắt của dữ liệu khách hàng.
* Phân tích phân phối của các biến phân loại chính: `LIFESTAGE` và `PREMIUM_CUSTOMER`.

### V. Hợp Nhất Dữ Liệu Giao Dịch và Khách Hàng

* Kết hợp dữ liệu giao dịch và khách hàng dựa trên `LYLTY_CARD_NBR` (số thẻ khách hàng thân thiết) để tạo một bộ dữ liệu toàn diện cho phân tích.
* Xác minh tính toàn vẹn của dữ liệu sau khi hợp nhất.

### VI. Phân Tích Phân Khúc Khách Hàng

* **Tổng Doanh Số**: Tính toán tổng doanh số cho từng phân khúc khách hàng (`LIFESTAGE` x `PREMIUM_CUSTOMER`).
* **Số Lượng Khách Hàng**: Đếm số lượng khách hàng duy nhất trong mỗi phân khúc.
* **Số Lượng Đơn Vị Trung Bình trên Mỗi Khách Hàng**: Phân tích số lượng sản phẩm trung bình mà mỗi khách hàng mua trong từng phân khúc.
* **Giá Trung Bình trên Mỗi Đơn Vị**: Tính toán giá trung bình cho mỗi đơn vị sản phẩm mua bởi các phân khúc khác nhau để hiểu hành vi định giá.
* **Kiểm Định Ý Nghĩa Thống Kê (T-test)**: Thực hiện kiểm định t để so sánh sự khác biệt có ý nghĩa thống kê về giá trung bình mỗi đơn vị giữa các phân khúc cụ thể (ví dụ: Young/Midage Singles/Couples - Mainstream vs. Budget/Premium).

### VII. Phân Tích Sâu: Phân Khúc 'Mainstream, Young Singles/Couples'

* Đi sâu vào phân khúc khách hàng mục tiêu để hiểu rõ hơn về sở thích của họ.
* **Phân tích Mức độ Ưa Thích Thương Hiệu**: So sánh tỷ lệ mua các thương hiệu khác nhau của phân khúc mục tiêu so với các phân khúc còn lại.
* **Phân tích Sở Thích Kích Thước Gói**: So sánh sở thích về kích thước gói sản phẩm của phân khúc mục tiêu.
* Xác định các sản phẩm cụ thể (thương hiệu và kích thước gói) được phân khúc này ưa chuộng.

## Kết Quả và Đề Xuất Chính

*Tổng hợp các phát hiện quan trọng từ phân tích của bạn ở đây. Ví dụ:*
* Phân khúc **"Young Singles/Couples - Mainstream"** và **"Midage Singles/Couples - Mainstream"** là những người chi tiêu nhiều nhất và có số lượng khách hàng lớn.
* Có bằng chứng thống kê cho thấy khách hàng **"Mainstream"** trong nhóm Young/Midage Singles/Couples có xu hướng trả giá mỗi đơn vị cao hơn so với các nhóm Budget/Premium cùng giai đoạn sống.
* Phân khúc **"Mainstream, Young Singles/Couples"** có mức độ ưa thích cao hơn đối với các sản phẩm có kích thước gói **270g** và các thương hiệu như **Grain Waves** và **Tyrrells**.

*Dựa trên những phát hiện này, các khuyến nghị có thể bao gồm:*
* Tập trung các chiến lược marketing vào các phân khúc khách hàng có doanh số và giá trị cao.
* Xem xét các chương trình khuyến mãi đặc biệt cho các sản phẩm kích thước gói 270g và các thương hiệu được ưa chuộng bởi phân khúc "Mainstream, Young Singles/Couples".
* Tiếp tục theo dõi hành vi mua sắm để điều chỉnh chiến lược sản phẩm và giá cả.

## Hướng Phát Triển Tương Lai

* Mở rộng phân tích để bao gồm các biến khách hàng khác.
* Áp dụng các kỹ thuật phân cụm nâng cao hơn.
* Xây dựng mô hình dự đoán hành vi khách hàng.



ENGLISH VER.
# QVI Transaction Data and Customer Behavior Analysis

## Introduction

This project is an in-depth data analysis of customer purchasing behavior and transaction data from QVI (Quantium Virtual Internship). The main goal is to explore consumption patterns, segment customers based on `LIFESTAGE` and `PREMIUM_CUSTOMER` categories, and subsequently provide business recommendations.

The project encompasses steps from raw data preprocessing, cleaning, feature engineering to exploratory analysis and data merging, culminating in a detailed analysis of potential customer segments.

## Datasets

The project utilizes two primary datasets:

1.  **`QVI_transaction_data.xlsx`**: Contains detailed information about purchases, including transaction date, product name, quantity, and total sales.
2.  **`QVI_purchase_behaviour.csv`**: Contains information about customer purchasing behavior, including `LIFESTAGE` and `PREMIUM_CUSTOMER` for each loyalty card number.

## Key Analysis Steps

The project is structured into the following main sections:

### I. Python Environment Setup and Data Loading

* Imports necessary libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy.stats`, `re`.
* Loads transaction and customer data into DataFrames.

### II. Transaction Data: Preprocessing and Exploratory Analysis

* **`DATE` Column Conversion**: Converts the date format from numerical to standard datetime.
* **`PROD_NAME` Analysis**:
    * Explores unique product names.
    * Removes irrelevant products (e.g., "Salsa").
* **Summary Statistics & Outlier Management**:
    * Checks initial descriptive statistics.
    * Identifies and handles outlier transactions (e.g., `PROD_QTY` = 200).
    * Removes customers with anomalous purchasing behavior.
* **Transaction Trends Over Time**:
    * Counts the number of transactions by day.
    * Identifies missing data dates (e.g., Christmas).
    * Visualizes transaction volume to identify temporal trends.

### III. Feature Engineering from Transaction Data

* **`PACK_SIZE` Extraction**: Extracts the pack size from product names for preference analysis.
* **`BRAND` Extraction and Cleaning**: Extracts brand names from product names and standardizes them for consistent analysis.

### IV. Customer Data: Exploration

* Checks the structure and summary statistics of the customer data.
* Analyzes the distribution of key categorical variables: `LIFESTAGE` and `PREMIUM_CUSTOMER`.

### V. Merging Transaction and Customer Data

* Combines transaction and customer data based on `LYLTY_CARD_NBR` (loyalty card number) to create a comprehensive dataset for analysis.
* Verifies data integrity after merging.

### VI. Customer Segment Analysis

* **Total Sales**: Calculates total sales for each customer segment (`LIFESTAGE` x `PREMIUM_CUSTOMER`).
* **Number of Customers**: Counts unique customers within each segment.
* **Average Units Per Customer**: Analyzes the average number of products purchased by each customer within each segment.
* **Average Price Per Unit**: Calculates the average price per unit of products purchased by different segments to understand pricing behavior.
* **Statistical Significance Test (T-test)**: Performs a t-test to compare statistically significant differences in average price per unit between specific segments (e.g., Young/Midage Singles/Couples - Mainstream vs. Budget/Premium).

### VII. Deep Dive: 'Mainstream, Young Singles/Couples' Segment

* Delves into a target customer segment to gain deeper insights into their preferences.
* **Brand Affinity Analysis**: Compares the proportion of different brands purchased by the target segment versus other segments.
* **Pack Size Preference Analysis**: Compares pack size preferences of the target segment.
* Identifies specific products (brands and pack sizes) favored by this segment.

## Key Findings and Recommendations

*Summarize your key findings from the analysis here. For example:*
* The **"Young Singles/Couples - Mainstream"** and **"Midage Singles/Couples - Mainstream"** segments are among the highest spenders and represent a significant customer base.
* There is statistical evidence suggesting that **"Mainstream"** customers within the Young/Midage Singles/Couples group tend to pay a significantly higher price per unit compared to their Budget/Premium counterparts in the same lifestage.
* The **"Mainstream, Young Singles/Couples"** segment shows higher affinity for **270g** pack sizes and brands like **Grain Waves** and **Tyrrells**.

*Based on these findings, recommendations could include:*
* Focus marketing strategies on high-value and high-volume customer segments.
* Consider special promotions for 270g pack sizes and favored brands by the "Mainstream, Young Singles/Couples" segment.
* Continuously monitor purchasing behavior to adapt product and pricing strategies.

## Future Enhancements

* Expand analysis to include other customer variables.
* Apply more advanced clustering techniques.
* Build predictive models for customer behavior.