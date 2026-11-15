
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

# =====================================================
# 1. PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="Superstore DSS",
    page_icon="📊",
    layout="wide"
)

# =====================================================
# 2. DATABASE CONNECTION
# =====================================================

def get_connection():
    return pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=LAPTOP-I8D3VRTA\\SQLEXPRESS;"
        "DATABASE=Superstore_DW;"
        "Trusted_Connection=yes;"
    )


@st.cache_data(ttl=300)
def load_data():
    conn = get_connection()

    query = """
    SELECT
        f.OrderID,
        f.Sales,
        f.Profit,
        f.Quantity,
        f.Discount,
        f.ShippingDays,

        d.Date AS OrderDate,
        d.Year,
        d.Quarter,
        d.Month,
        d.MonthName,

        p.ProductID,
        p.ProductName,
        p.Category,
        p.SubCategory,

        c.CustomerID,
        c.CustomerName,
        c.Segment,

        l.Region,
        l.State,
        l.City,

        sm.ShipMode

    FROM Fact_Sales f

    JOIN Dim_Date d
        ON f.OrderDateKey = d.DateKey

    JOIN Dim_Product p
        ON f.ProductKey = p.ProductKey

    JOIN Dim_Customer c
        ON f.CustomerKey = c.CustomerKey

    JOIN Dim_Location l
        ON f.LocationKey = l.LocationKey

    JOIN Dim_ShipMode sm
        ON f.ShipModeKey = sm.ShipModeKey;
    """

    try:
        df = pd.read_sql_query(query, conn)
    finally:
        conn.close()

    df["OrderDate"] = pd.to_datetime(df["OrderDate"])

    return df


# =====================================================
# 3. LOAD DATA
# =====================================================

st.title("📊 Superstore Decision Support System")
st.caption("Sales Performance Analysis | Data Warehouse: Superstore_DW")

try:
    df = load_data()

except Exception as e:
    st.error(f"Cannot load data from SQL Server: {e}")
    st.stop()


# =====================================================
# 4. SIDEBAR FILTERS
# =====================================================

st.sidebar.title("🔎 Data Filters")

st.sidebar.caption("Các bộ lọc áp dụng cho toàn bộ dashboard.")

min_date = df["OrderDate"].min().date()
max_date = df["OrderDate"].max().date()

selected_dates = st.sidebar.date_input(
    "Order Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

regions = sorted(df["Region"].dropna().unique())
categories = sorted(df["Category"].dropna().unique())
segments = sorted(df["Segment"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Region",
    options=regions,
    default=regions
)

selected_categories = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=categories
)

selected_segments = st.sidebar.multiselect(
    "Customer Segment",
    options=segments,
    default=segments
)

# =====================================================
# 5. APPLY FILTERS
# =====================================================

filtered_df = df.copy()

if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered_df = filtered_df[
        (filtered_df["OrderDate"].dt.date >= start_date) &
        (filtered_df["OrderDate"].dt.date <= end_date)
    ]

if selected_regions:
    filtered_df = filtered_df[
        filtered_df["Region"].isin(selected_regions)
    ]

if selected_categories:
    filtered_df = filtered_df[
        filtered_df["Category"].isin(selected_categories)
    ]

if selected_segments:
    filtered_df = filtered_df[
        filtered_df["Segment"].isin(selected_segments)
    ]


# =====================================================
# 6. HELPER FUNCTIONS
# =====================================================

def calculate_kpis(data):
    total_sales = data["Sales"].sum()
    total_profit = data["Profit"].sum()
    total_quantity = data["Quantity"].sum()
    total_orders = data["OrderID"].nunique()

    profit_margin = (
        total_profit / total_sales * 100
        if total_sales != 0 else 0
    )

    return {
        "sales": total_sales,
        "profit": total_profit,
        "quantity": total_quantity,
        "orders": total_orders,
        "margin": profit_margin
    }


def show_kpis(data):
    kpis = calculate_kpis(data)

    # Chia KPI thành hai hàng để tránh bị cắt chữ
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Sales",
        f"${kpis['sales']:,.2f}"
    )

    col2.metric(
        "Total Profit",
        f"${kpis['profit']:,.2f}"
    )

    col3.metric(
        "Total Orders",
        f"{kpis['orders']:,}"
    )

    col4, col5 = st.columns(2)

    col4.metric(
        "Total Quantity",
        f"{kpis['quantity']:,}"
    )

    col5.metric(
        "Profit Margin",
        f"{kpis['margin']:.2f}%"
    )


# =====================================================
# 7. DASHBOARD TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Overview",
    "📈 Sales Trends",
    "📦 Products",
    "🌎 Regions",
    "👥 Customers",
    "💡 Decision Support"
])


# =====================================================
# TAB 1: OVERVIEW
# =====================================================

with tab1:

    st.header("Sales Overview")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        show_kpis(filtered_df)

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Sales by Year")

            yearly = (
                filtered_df
                .groupby("Year", as_index=False)["Sales"]
                .sum()
                .sort_values("Year")
            )

            fig = px.bar(
                yearly,
                x="Year",
                y="Sales",
                title="Annual Sales",
                text_auto=".2s"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Sales by Category")

            category_data = (
                filtered_df
                .groupby("Category", as_index=False)["Sales"]
                .sum()
                .sort_values("Sales", ascending=False)
            )

            fig = px.pie(
                category_data,
                names="Category",
                values="Sales",
                hole=0.4,
                title="Sales Distribution"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent Sales Records")

        st.dataframe(
            filtered_df[
                [
                    "OrderID",
                    "OrderDate",
                    "ProductName",
                    "Category",
                    "Region",
                    "Sales",
                    "Profit"
                ]
            ].sort_values("OrderDate", ascending=False).head(10),
            use_container_width=True
        )


# =====================================================
# TAB 2: SALES TRENDS
# =====================================================

with tab2:

    st.header("Sales Trend Analysis")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        monthly = filtered_df.copy()

        monthly["MonthStart"] = (
            monthly["OrderDate"]
            .dt.to_period("M")
            .dt.to_timestamp()
        )

        monthly_data = (
            monthly
            .groupby("MonthStart", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("MonthStart")
        )

        metric_choice = st.selectbox(
            "Select metric",
            ["Sales", "Profit"]
        )

        fig = px.line(
            monthly_data,
            x="MonthStart",
            y=metric_choice,
            markers=True,
            title=f"Monthly {metric_choice} Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Yearly Performance")

        yearly = (
            filtered_df
            .groupby("Year", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum")
            )
            .sort_values("Year")
        )

        yearly["SalesGrowthRate"] = (
            yearly["Sales"].pct_change() * 100
        )

        st.dataframe(
            yearly.round(2),
            use_container_width=True
        )


# =====================================================
# TAB 3: PRODUCT ANALYSIS
# =====================================================

with tab3:

    st.header("Product Performance Analysis")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        product_data = (
            filtered_df
            .groupby(
                ["Category", "SubCategory"],
                as_index=False
            )
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Quantity=("Quantity", "sum")
            )
        )

        product_data["ProfitMargin"] = (
            product_data["Profit"] /
            product_data["Sales"].replace(0, float("nan")) * 100
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                product_data,
                x="Category",
                y="Sales",
                color="SubCategory",
                title="Sales by Category and SubCategory"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                product_data,
                x="SubCategory",
                y="Profit",
                color="Profit",
                title="Profit by SubCategory"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Product Performance Details")

        st.dataframe(
            product_data.sort_values("Sales", ascending=False).round(2),
            use_container_width=True
        )


# =====================================================
# TAB 4: REGIONAL ANALYSIS
# =====================================================

with tab4:

    st.header("Regional Performance Analysis")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        region_data = (
            filtered_df
            .groupby("Region", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.bar(
                region_data,
                x="Region",
                y="Sales",
                color="Region",
                title="Sales by Region"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                region_data,
                x="Region",
                y="Profit",
                color="Profit",
                title="Profit by Region"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("State Performance")

        state_data = (
            filtered_df
            .groupby("State", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("Sales", ascending=False)
            .head(15)
        )

        fig = px.bar(
            state_data,
            x="Sales",
            y="State",
            orientation="h",
            color="Profit",
            title="Top 15 States by Sales"
        )

        st.plotly_chart(fig, use_container_width=True)


# =====================================================
# TAB 5: CUSTOMER ANALYSIS
# =====================================================

with tab5:

    st.header("Customer Analysis")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        segment_data = (
            filtered_df
            .groupby("Segment", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Customers=("CustomerID", "nunique")
            )
        )

        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                segment_data,
                names="Segment",
                values="Sales",
                hole=0.4,
                title="Sales by Customer Segment"
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                segment_data,
                x="Segment",
                y="Profit",
                color="Segment",
                title="Profit by Customer Segment"
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top 10 Customers")

        customer_data = (
            filtered_df
            .groupby("CustomerName", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
            .sort_values("Sales", ascending=False)
            .head(10)
        )

        st.dataframe(
            customer_data.round(2),
            use_container_width=True
        )


# =====================================================
# TAB 6: DECISION SUPPORT
# =====================================================

with tab6:

    st.header("Decision Support Center")

    if filtered_df.empty:
        st.warning("Không có dữ liệu phù hợp với bộ lọc.")
    else:
        kpis = calculate_kpis(filtered_df)

        st.subheader("Business Performance Status")

        if kpis["profit"] < 0:
            st.error(
                "Tổng lợi nhuận đang âm. "
                "Cần xem xét các nhóm sản phẩm và khu vực thua lỗ."
            )

        elif kpis["margin"] < 10:
            st.warning(
                "Biên lợi nhuận dưới 10%. "
                "Nên kiểm tra chi phí, mức giảm giá và cơ cấu sản phẩm."
            )

        else:
            st.success(
                "Tổng lợi nhuận đang dương và biên lợi nhuận đạt từ 10%."
            )

        st.divider()

        st.subheader("Loss-making SubCategories")

        loss_data = (
            filtered_df
            .groupby("SubCategory", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        loss_data = loss_data[
            loss_data["Profit"] < 0
        ].sort_values("Profit")

        if loss_data.empty:
            st.success("Không có SubCategory nào bị lỗ trong dữ liệu đã lọc.")
        else:
            st.warning(
                "Các nhóm sản phẩm dưới đây có tổng lợi nhuận âm."
            )

            st.dataframe(
                loss_data.round(2),
                use_container_width=True
            )

        st.divider()

        st.subheader("Regional Warning")

        loss_region = (
            filtered_df
            .groupby("Region", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum")
            )
        )

        loss_region = loss_region[
            loss_region["Profit"] < 0
        ]

        if loss_region.empty:
            st.success("Không có khu vực nào có tổng lợi nhuận âm.")
        else:
            st.dataframe(
                loss_region.round(2),
                use_container_width=True
            )

        st.divider()

        st.subheader("Discount Analysis")

        discount_data = (
            filtered_df
            .groupby("Discount", as_index=False)
            .agg(
                Sales=("Sales", "sum"),
                Profit=("Profit", "sum"),
                Records=("OrderID", "count")
            )
            .sort_values("Discount")
        )

        fig = px.bar(
            discount_data,
            x="Discount",
            y="Profit",
            color="Profit",
            title="Profit by Discount Level"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Các cảnh báo là quy tắc phân tích đơn giản dựa trên dữ liệu đã lọc, "
            "không phải kết luận về quan hệ nhân quả."
        )


# =====================================================
# 8. FOOTER
# =====================================================

st.divider()

st.caption(
    "Superstore DSS | SQL Server Data Warehouse | "
    "Developed with Python and Streamlit"
)

# Download filtered data
st.sidebar.divider()

st.sidebar.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False).encode("utf-8-sig"),
    file_name="superstore_filtered_data.csv",
    mime="text/csv"
)

if st.sidebar.button("🔄 Refresh Data"):
    load_data.clear()
    st.rerun()
