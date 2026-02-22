import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 E-Commerce Sales Dashboard")
st.markdown("### Real-time performance overview of e-commerce sales")

# -------------------------------------------------
# LOAD DATA (SAFE + CLEAN)
# -------------------------------------------------
@st.cache_data
def load_data():
    file_path = Path("ECOM sales.csv")

    if not file_path.exists():
        st.error("❌ CSV file not found. Put 'ECOM sales.csv' in the project folder.")
        st.stop()

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"❌ Error reading CSV: {e}")
        st.stop()

    # 🔥 CLEAN COLUMN NAMES
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(" ", "_")

    # Try to detect date column automatically
    for col in df.columns:
        if "date" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df.rename(columns={col: "Order_Date"}, inplace=True)
                break
            except:
                pass

    return df

df = load_data()

# -------------------------------------------------
# CHECK REQUIRED COLUMNS
# -------------------------------------------------
required_cols = ["Region", "Category", "Sales", "Profit", "Quantity"]

missing = [col for col in required_cols if col not in df.columns]

if missing:
    st.error(f"❌ Missing columns in CSV: {missing}")
    st.write("📌 Your columns are:", list(df.columns))
    st.stop()

# -------------------------------------------------
# SIDEBAR FILTERS
# -------------------------------------------------
st.sidebar.header("🔍 Filters")

region_filter = st.sidebar.multiselect(
    "Select Region",
    options=sorted(df["Region"].dropna().unique()),
    default=sorted(df["Region"].dropna().unique())
)

category_filter = st.sidebar.multiselect(
    "Select Category",
    options=sorted(df["Category"].dropna().unique()),
    default=sorted(df["Category"].dropna().unique())
)

filtered_df = df[
    (df["Region"].isin(region_filter)) &
    (df["Category"].isin(category_filter))
]

# -------------------------------------------------
# DATE FILTER (ONLY IF PRESENT)
# -------------------------------------------------
if "Order_Date" in filtered_df.columns:
    min_date = filtered_df["Order_Date"].min()
    max_date = filtered_df["Order_Date"].max()

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date]
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Order_Date"] >= pd.to_datetime(start_date)) &
            (filtered_df["Order_Date"] <= pd.to_datetime(end_date))
        ]

# -------------------------------------------------
# KPI METRICS
# -------------------------------------------------
col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"₹{filtered_df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"₹{filtered_df['Profit'].sum():,.0f}")
col3.metric("Total Quantity", f"{filtered_df['Quantity'].sum():,.0f}")

st.divider()

# -------------------------------------------------
# SALES BY CATEGORY (BAR)
# -------------------------------------------------
sales_by_cat = (
    filtered_df.groupby("Category")["Sales"]
    .sum()
    .reset_index()
)

fig_bar = px.bar(
    sales_by_cat,
    x="Category",
    y="Sales",
    title="Sales by Category"
)

st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------
# SALES BY REGION (PIE)
# -------------------------------------------------
sales_by_region = (
    filtered_df.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

fig_pie = px.pie(
    sales_by_region,
    names="Region",
    values="Sales",
    title="Sales Distribution by Region"
)

st.plotly_chart(fig_pie, use_container_width=True)

# -------------------------------------------------
# SALES TREND (VERY PROFESSIONAL)
# -------------------------------------------------
if "Order_Date" in filtered_df.columns:
    st.subheader("📈 Sales Trend Over Time")

    trend_df = (
        filtered_df.groupby("Order_Date")["Sales"]
        .sum()
        .reset_index()
        .sort_values("Order_Date")
    )

    fig_line = px.line(
        trend_df,
        x="Order_Date",
        y="Sales",
        markers=True
    )

    st.plotly_chart(fig_line, use_container_width=True)

# -------------------------------------------------
# DOWNLOAD BUTTON
# -------------------------------------------------
st.subheader("⬇️ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download CSV",
    data=csv,
    file_name="filtered_ecommerce_data.csv",
    mime="text/csv"
)

# -------------------------------------------------
# DATA PREVIEW
# -------------------------------------------------
st.subheader("🔎 Data Preview")
st.dataframe(filtered_df, use_container_width=True)
