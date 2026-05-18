"""
E-Commerce Sales & Customer Analytics Dashboard
A professional, enterprise-grade analytics dashboard built with Streamlit and Plotly.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings('ignore')

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM STYLING ====================
def apply_dark_theme():
    """Apply professional dark theme styling"""
    st.markdown("""
    <style>
        * {
            margin: 0;
            padding: 0;
        }
        
        body {
            background-color: #0e1117;
            color: #c9d1d9;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }
        
        .main {
            background-color: #0e1117;
            padding: 2rem 1rem;
        }
        
        .stMetric {
            background-color: #161b22;
            padding: 1.5rem;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #161b22 0%, #0d1117 100%);
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid #58a6ff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        }
        
        h1, h2, h3 {
            color: #f0f6fc;
            font-weight: 600;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #c9d1d9;
            padding: 0.5rem 1rem;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1f6feb;
            color: #ffffff;
        }
        
        .stSelectbox, .stMultiSelect, .stDateInput {
            background-color: #0d1117;
        }
        
        .stSidebar {
            background-color: #0d1117;
            border-right: 1px solid #30363d;
        }
        
        .sidebar-section {
            background-color: #161b22;
            padding: 1rem;
            border-radius: 6px;
            margin-bottom: 1rem;
            border: 1px solid #30363d;
        }
    </style>
    """, unsafe_allow_html=True)

apply_dark_theme()

# ==================== DATA LOADING & CACHING ====================
@st.cache_data
def load_data():
    """Load and cache the superstore dataset"""
    data_path = Path(__file__).resolve().parent / 'superstore.csv'

    if not data_path.exists():
        st.error(
            "Dataset file not found. Please ensure superstore.csv is in the project directory."
        )
        return None

    try:
        df = pd.read_csv(data_path, encoding='latin1')
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None

    required_columns = [
        'Row ID', 'Order ID', 'Order Date', 'Ship Date', 'Ship Mode',
        'Customer ID', 'Customer Name', 'Segment', 'Country', 'City',
        'State', 'Postal Code', 'Region', 'Product ID', 'Category',
        'Sub-Category', 'Product Name', 'Sales', 'Quantity', 'Discount', 'Profit'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        st.error(
            f"Dataset is missing required columns: {', '.join(missing_columns)}"
        )
        return None

    return df

def parse_date_column(series, column_name):
    """Parse a date column using multiple fallback methods."""
    parsed = pd.to_datetime(series, format='%m/%d/%Y', errors='coerce')
    if parsed.isna().any():
        parsed = pd.to_datetime(series, infer_datetime_format=True, errors='coerce')
    if parsed.isna().any():
        raise ValueError(f"Unable to parse dates in '{column_name}'. Please verify the format.")
    return parsed

@st.cache_data
def clean_data(df):
    """Clean and prepare the dataset"""
    df_clean = df.copy()

    # Convert date columns using robust parsing
    try:
        df_clean['Order Date'] = parse_date_column(df_clean['Order Date'], 'Order Date')
        df_clean['Ship Date'] = parse_date_column(df_clean['Ship Date'], 'Ship Date')
    except Exception as e:
        st.error(str(e))
        return pd.DataFrame()

    # Create additional calculated fields
    df_clean['Days to Ship'] = (df_clean['Ship Date'] - df_clean['Order Date']).dt.days
    df_clean['Year'] = df_clean['Order Date'].dt.year
    df_clean['Month'] = df_clean['Order Date'].dt.month
    df_clean['Month Name'] = df_clean['Order Date'].dt.strftime('%B')
    df_clean['Quarter'] = 'Q' + df_clean['Order Date'].dt.quarter.astype(str)
    df_clean['Week'] = df_clean['Order Date'].dt.isocalendar().week.astype(int)
    df_clean['Profit Ratio'] = np.where(
        df_clean['Sales'] != 0,
        df_clean['Profit'] / df_clean['Sales'] * 100,
        0
    ).round(2)

    # Remove duplicates (if any)
    df_clean = df_clean.drop_duplicates(subset=['Row ID'])

    if df_clean.empty:
        st.error("The cleaned dataset contains no records after validation.")

    return df_clean

# ==================== LOAD DATA ====================
df = load_data()
if df is None or df.empty:
    st.stop()

df = clean_data(df)
if df.empty:
    st.stop()

# ==================== SIDEBAR - FILTERS & NAVIGATION ====================
with st.sidebar:
    st.markdown("### 📊 Dashboard Controls")
    
    # Navigation
    page = st.radio(
        "Select View",
        ["📈 Business Overview", "💰 Sales Analysis", "👥 Customer Insights", 
         "📦 Product Performance", "🌍 Regional Analysis", "🤖 Sales Forecasting"],
        key="page_selector"
    )
    
    st.markdown("---")
    st.markdown("### 🔍 Filters")
    
    # Date Range Filter
    min_date = df['Order Date'].min().to_pydatetime()
    max_date = df['Order Date'].max().to_pydatetime()
    
    date_range = st.slider(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        format="MMM DD, YYYY"
    )
    
    # Region Filter
    regions = st.multiselect(
        "Select Region(s)",
        options=sorted(df['Region'].unique()),
        default=sorted(df['Region'].unique())
    )
    
    # Category Filter
    categories = st.multiselect(
        "Select Category(ies)",
        options=sorted(df['Category'].unique()),
        default=sorted(df['Category'].unique())
    )
    
    # Segment Filter
    segments = st.multiselect(
        "Select Segment(s)",
        options=sorted(df['Segment'].unique()),
        default=sorted(df['Segment'].unique())
    )
    
    # Ship Mode Filter
    ship_modes = st.multiselect(
        "Select Ship Mode(s)",
        options=sorted(df['Ship Mode'].unique()),
        default=sorted(df['Ship Mode'].unique())
    )

# ==================== APPLY FILTERS ====================
df_filtered = df[
    (df['Order Date'] >= date_range[0]) & 
    (df['Order Date'] <= date_range[1]) &
    (df['Region'].isin(regions)) &
    (df['Category'].isin(categories)) &
    (df['Segment'].isin(segments)) &
    (df['Ship Mode'].isin(ship_modes))
].copy()

if df_filtered.empty:
    st.warning(
        "No data matches the selected filter values. Please adjust the date range or filter selections."
    )
    st.stop()

# ==================== HELPER FUNCTIONS ====================
def format_number(value):
    """Format large numbers for display"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    if not np.isfinite(value):
        return "-"
    if abs(value) >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif abs(value) >= 1_000:
        return f"${value/1_000:.1f}K"
    return f"${value:,.0f}"

def format_percentage(value):
    """Format percentage values"""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    if not np.isfinite(value):
        return "-"
    return f"{value:.1f}%"


def prepare_monthly_sales(df):
    """Aggregate sales into a monthly time series."""
    monthly = df.copy()
    monthly['Month Start'] = monthly['Order Date'].dt.to_period('M').dt.to_timestamp()
    monthly_sales = (
        monthly.groupby('Month Start', observed=True)['Sales']
        .sum()
        .reset_index()
        .sort_values('Month Start')
    )
    monthly_sales['Month Index'] = np.arange(len(monthly_sales))
    return monthly_sales


def train_random_forest_forecast(monthly_sales, future_periods=6):
    """Train a Random Forest regression model and produce a dynamic future forecast.

    The forecast is recalculated inside this function for every new slider value.
    Future months are built from scratch, with autoregressive lag features and seasonal
    month cycles generated dynamically for each forecast horizon.
    """
    monthly_sales = monthly_sales.copy()
    monthly_sales['Month'] = monthly_sales['Month Start'].dt.month
    monthly_sales['Month_Sin'] = np.sin(2 * np.pi * monthly_sales['Month'] / 12)
    monthly_sales['Month_Cos'] = np.cos(2 * np.pi * monthly_sales['Month'] / 12)

    # Build autoregressive features to improve trend prediction.
    for lag in [1, 2, 3]:
        monthly_sales[f'Lag_{lag}'] = monthly_sales['Sales'].shift(lag)
    monthly_sales['RollingMean_3'] = monthly_sales['Sales'].rolling(3).mean()
    feature_df = monthly_sales.dropna().reset_index(drop=True)

    if len(feature_df) < 6:
        raise ValueError("Not enough monthly history available for forecasting.")

    feature_columns = [
        'Month Index', 'Month_Sin', 'Month_Cos',
        'Lag_1', 'Lag_2', 'Lag_3', 'RollingMean_3'
    ]
    X = feature_df[feature_columns].values
    y = feature_df['Sales'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    r2_score = model.score(X_test, y_test)

    last_month = monthly_sales['Month Start'].max()
    future_dates = pd.date_range(
        start=last_month + pd.offsets.MonthBegin(1),
        periods=future_periods,
        freq='MS'
    )

    # Use the last known values to bootstrap auto-regressive forecasting.
    recent_sales = monthly_sales['Sales'].tolist()[-3:]
    future_sales = []
    future_index = np.arange(len(monthly_sales), len(monthly_sales) + future_periods)

    for step, future_date in enumerate(future_dates):
        month = future_date.month
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)
        lag_1 = recent_sales[-1]
        lag_2 = recent_sales[-2]
        lag_3 = recent_sales[-3]
        rolling_mean_3 = np.mean(recent_sales[-3:])

        future_row = np.array([
            future_index[step], month_sin, month_cos,
            lag_1, lag_2, lag_3, rolling_mean_3
        ]).reshape(1, -1)

        prediction = model.predict(future_row)[0]
        future_sales.append(prediction)
        recent_sales.append(prediction)

    forecast_df = pd.DataFrame({
        'Month Start': future_dates,
        'Sales': future_sales,
        'Month Index': future_index
    })

    return model, r2_score, forecast_df


def create_kpi_card(label, value, metric_type="currency", delta=None):
    """Create a styled KPI card"""
    if metric_type == "currency":
        value_str = format_number(value)
    elif metric_type == "percentage":
        value_str = format_percentage(value)
    else:
        value_str = format_number(value)
    
    if delta is None or (isinstance(delta, float) and np.isnan(delta)):
        delta_str = ""
    else:
        delta_str = f"{'📈' if delta >= 0 else '📉'} {delta:.1f}%"
    
    return f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: #8b949e; font-weight: 500;">{label}</div>
        <div style="font-size: 1.8rem; color: #58a6ff; font-weight: 700; margin: 0.5rem 0;">{value_str}</div>
        <div style="font-size: 0.85rem; color: #79c0ff;">{delta_str}</div>
    </div>
    """

def plot_template_config():
    """Return professional Plotly template configuration"""
    return {
        'template': 'plotly_dark',
        'plot_bgcolor': '#161b22',
        'paper_bgcolor': '#0e1117',
        'font': {'family': 'Arial, sans-serif', 'color': '#c9d1d9', 'size': 11},
        'hovermode': 'x unified'
    }

# ==================== PAGE 1: BUSINESS OVERVIEW ====================
if page == "📈 Business Overview":
    st.title("📊 Business Overview")
    st.markdown("---")
    
    # Calculate KPIs
    total_sales = df_filtered['Sales'].sum()
    total_profit = df_filtered['Profit'].sum()
    total_orders = df_filtered['Order ID'].nunique()
    profit_ratio = (total_profit / total_sales * 100) if total_sales > 0 else 0
    
    # Calculate deltas (comparing current period to previous period)
    mid_date = (date_range[0] + (date_range[1] - date_range[0]) / 2)
    df_current = df_filtered[df_filtered['Order Date'] >= mid_date]
    df_previous = df_filtered[df_filtered['Order Date'] < mid_date]
    
    delta_sales = ((df_current['Sales'].sum() / df_previous['Sales'].sum() - 1) * 100) if df_previous['Sales'].sum() > 0 else 0
    delta_profit = ((df_current['Profit'].sum() / df_previous['Profit'].sum() - 1) * 100) if df_previous['Profit'].sum() > 0 else 0
    
    # Display KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_kpi_card("Total Sales", total_sales, "currency", delta_sales), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_kpi_card("Total Profit", total_profit, "currency", delta_profit), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_kpi_card("Total Orders", total_orders, "number"), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_kpi_card("Profit Ratio", profit_ratio, "percentage"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main metrics visualizations
    col1, col2 = st.columns(2)
    
    # Sales Trend
    with col1:
        sales_trend = df_filtered.groupby(df_filtered['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
        sales_trend['Order Date'] = sales_trend['Order Date'].astype(str)
        
        fig = px.line(
            sales_trend,
            x='Order Date',
            y='Sales',
            title='Monthly Sales Trend',
            markers=True,
            line_shape='spline'
        )
        fig.update_layout(
            height=400,
            **plot_template_config(),
            xaxis_title='Month',
            yaxis_title='Sales ($)'
        )
        fig.update_traces(line_color='#58a6ff', marker_color='#79c0ff')
        st.plotly_chart(fig, use_container_width=True)
    
    # Profit Trend
    with col2:
        profit_trend = df_filtered.groupby(df_filtered['Order Date'].dt.to_period('M'))['Profit'].sum().reset_index()
        profit_trend['Order Date'] = profit_trend['Order Date'].astype(str)
        
        fig = px.line(
            profit_trend,
            x='Order Date',
            y='Profit',
            title='Monthly Profit Trend',
            markers=True,
            line_shape='spline'
        )
        fig.update_layout(
            height=400,
            **plot_template_config(),
            xaxis_title='Month',
            yaxis_title='Profit ($)'
        )
        fig.update_traces(line_color='#3fb950', marker_color='#56d364')
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Category & Segment Distribution
    col1, col2 = st.columns(2)
    
    with col1:
        category_sales = df_filtered.groupby('Category')['Sales'].sum().sort_values(ascending=False)
        
        fig = px.pie(
            values=category_sales.values,
            names=category_sales.index,
            title='Sales Distribution by Category',
            hole=0.4
        )
        fig.update_layout(height=400, **plot_template_config())
        fig.update_traces(
            marker_colors=['#58a6ff', '#3fb950', '#d29922'],
            textposition='inside',
            textinfo='label+percent'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        segment_sales = df_filtered.groupby('Segment')['Sales'].sum().sort_values(ascending=False)
        
        fig = px.pie(
            values=segment_sales.values,
            names=segment_sales.index,
            title='Sales Distribution by Segment',
            hole=0.4
        )
        fig.update_layout(height=400, **plot_template_config())
        fig.update_traces(
            marker_colors=['#58a6ff', '#79c0ff', '#1f6feb'],
            textposition='inside',
            textinfo='label+percent'
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 2: SALES ANALYSIS ====================
elif page == "💰 Sales Analysis":
    st.title("💰 Sales Analysis")
    st.markdown("---")
    
    # Sales Summary Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_order_value = df_filtered['Sales'].sum() / df_filtered['Order ID'].nunique()
        st.markdown(create_kpi_card("Avg Order Value", avg_order_value, "currency"), unsafe_allow_html=True)
    
    with col2:
        avg_discount = df_filtered['Discount'].mean() * 100
        st.markdown(create_kpi_card("Avg Discount", avg_discount, "percentage"), unsafe_allow_html=True)
    
    with col3:
        total_units = df_filtered['Quantity'].sum()
        st.markdown(create_kpi_card("Total Units Sold", total_units, "number"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sales Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["By Category", "By Region", "By Sub-Category", "By Ship Mode"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            category_data = df_filtered.groupby('Category').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Order ID': 'nunique'
            }).sort_values('Sales', ascending=True)
            
            fig = px.bar(
                category_data,
                x='Sales',
                y=category_data.index,
                orientation='h',
                title='Sales by Category',
                text_auto='.0f',
                color='Sales',
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                category_data,
                x='Profit',
                y=category_data.index,
                orientation='h',
                title='Profit by Category',
                text_auto='.0f',
                color='Profit',
                color_continuous_scale=['#0d1117', '#3fb950']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            region_data = df_filtered.groupby('Region').agg({
                'Sales': 'sum',
                'Profit': 'sum'
            }).sort_values('Sales', ascending=True)
            
            fig = px.bar(
                region_data,
                x='Sales',
                y=region_data.index,
                orientation='h',
                title='Sales by Region',
                text_auto='.0f',
                color='Sales',
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                region_data,
                x='Profit',
                y=region_data.index,
                orientation='h',
                title='Profit by Region',
                text_auto='.0f',
                color='Profit',
                color_continuous_scale=['#0d1117', '#3fb950']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        subcategory_data = df_filtered.groupby('Sub-Category').agg({
            'Sales': 'sum',
            'Profit': 'sum'
        }).sort_values('Sales', ascending=False).head(15)
        
        fig = px.bar(
            subcategory_data,
            title='Top 15 Sub-Categories by Sales',
            barmode='group',
            text_auto='.0f'
        )
        fig.update_layout(height=500, **plot_template_config())
        fig.update_traces(marker_color=['#58a6ff', '#3fb950'])
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        ship_data = df_filtered.groupby('Ship Mode').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Days to Ship': 'mean'
        }).sort_values('Sales', ascending=True)
        
        fig = px.bar(
            ship_data,
            x='Sales',
            y=ship_data.index,
            orientation='h',
            title='Sales by Ship Mode',
            text_auto='.0f',
            color='Sales',
            color_continuous_scale=['#0d1117', '#58a6ff']
        )
        fig.update_layout(height=300, **plot_template_config(), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Discount vs Profit Analysis
    st.subheader("📊 Discount Impact Analysis")
    
    discount_bins = pd.cut(df_filtered['Discount'], bins=[0, 0.1, 0.2, 0.3, 0.5], include_lowest=True)
    discount_analysis = df_filtered.groupby(discount_bins, observed=True).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Profit Ratio': 'mean',
        'Order ID': 'count'
    }).reset_index()
    discount_analysis['Discount'] = discount_analysis['Discount'].astype(str)
    
    fig = go.Figure(data=[
        go.Bar(name='Sales', x=discount_analysis['Discount'], y=discount_analysis['Sales'], marker_color='#58a6ff'),
        go.Bar(name='Profit', x=discount_analysis['Discount'], y=discount_analysis['Profit'], marker_color='#3fb950')
    ])
    fig.update_layout(
        title='Sales & Profit by Discount Range',
        barmode='group',
        height=400,
        **plot_template_config(),
        xaxis_title='Discount Range',
        yaxis_title='Amount ($)'
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 3: CUSTOMER INSIGHTS ====================
elif page == "👥 Customer Insights":
    st.title("👥 Customer Insights")
    st.markdown("---")
    
    # Customer Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_customers = df_filtered['Customer ID'].nunique()
        st.markdown(create_kpi_card("Unique Customers", unique_customers, "number"), unsafe_allow_html=True)
    
    with col2:
        repeat_customers = df_filtered.groupby('Customer ID').size()
        repeat_count = (repeat_customers > 1).sum()
        st.markdown(create_kpi_card("Repeat Customers", repeat_count, "number"), unsafe_allow_html=True)
    
    with col3:
        avg_customer_value = df_filtered.groupby('Customer ID')['Sales'].sum().mean()
        st.markdown(create_kpi_card("Avg Customer Value", avg_customer_value, "currency"), unsafe_allow_html=True)
    
    with col4:
        customers_by_segment = df_filtered.groupby('Segment')['Customer ID'].nunique()
        st.markdown(create_kpi_card("Segments", len(customers_by_segment), "number"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Customer Analysis Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Top Customers", "Segment Analysis", "Customer Distribution", "RFM Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            top_customers = df_filtered.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=top_customers.values,
                y=top_customers.index,
                orientation='h',
                title='Top 10 Customers by Sales',
                text_auto='.0f',
                color=top_customers.values,
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False, yaxis_title="", xaxis_title="Sales ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_profit_customers = df_filtered.groupby('Customer Name')['Profit'].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=top_profit_customers.values,
                y=top_profit_customers.index,
                orientation='h',
                title='Top 10 Customers by Profit',
                text_auto='.0f',
                color=top_profit_customers.values,
                color_continuous_scale=['#0d1117', '#3fb950']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False, yaxis_title="", xaxis_title="Profit ($)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            segment_metrics = df_filtered.groupby('Segment').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Customer ID': 'nunique',
                'Order ID': 'nunique'
            }).sort_values('Sales', ascending=False)
            
            fig = px.bar(
                segment_metrics,
                title='Segment Performance Metrics',
                barmode='group',
                text_auto='.0f',
                labels={'value': 'Amount', 'index': 'Segment'}
            )
            fig.update_layout(height=400, **plot_template_config())
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            segment_profit_ratio = (df_filtered.groupby('Segment')['Profit'].sum() / 
                                   df_filtered.groupby('Segment')['Sales'].sum() * 100).sort_values(ascending=False)
            
            fig = px.bar(
                x=segment_profit_ratio.index,
                y=segment_profit_ratio.values,
                title='Profit Ratio by Segment',
                text_auto='.1f',
                color=segment_profit_ratio.values,
                color_continuous_scale=['#d29922', '#3fb950']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False, yaxis_title="Profit Ratio (%)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            customers_by_segment = df_filtered.groupby('Segment')['Customer ID'].nunique()
            
            fig = px.pie(
                values=customers_by_segment.values,
                names=customers_by_segment.index,
                title='Customer Distribution by Segment',
                hole=0.4
            )
            fig.update_layout(height=400, **plot_template_config())
            fig.update_traces(
                marker_colors=['#58a6ff', '#79c0ff', '#1f6feb'],
                textposition='inside',
                textinfo='label+percent'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            customers_by_region = df_filtered.groupby('Region')['Customer ID'].nunique().sort_values(ascending=True)
            
            fig = px.bar(
                x=customers_by_region.values,
                y=customers_by_region.index,
                orientation='h',
                title='Customers by Region',
                text_auto='.0f',
                color=customers_by_region.values,
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False, xaxis_title="# Customers")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        # RFM Analysis
        rfm_data = df_filtered.groupby('Customer ID').agg({
            'Order Date': 'max',
            'Order ID': 'count',
            'Sales': 'sum'
        }).reset_index()
        
        rfm_data.columns = ['Customer ID', 'Last Purchase', 'Frequency', 'Monetary']
        
        max_date = df_filtered['Order Date'].max()
        rfm_data['Recency'] = (max_date - rfm_data['Last Purchase']).dt.days
        
        # Create RFM Score
        rfm_data['R_Score'] = pd.qcut(rfm_data['Recency'], q=4, labels=[4, 3, 2, 1], duplicates='drop')
        rfm_data['F_Score'] = pd.qcut(rfm_data['Frequency'].rank(method='first'), q=4, labels=[1, 2, 3, 4], duplicates='drop')
        rfm_data['M_Score'] = pd.qcut(rfm_data['Monetary'], q=4, labels=[1, 2, 3, 4], duplicates='drop')
        
        rfm_data['RFM_Score'] = rfm_data['R_Score'].astype(str) + rfm_data['F_Score'].astype(str) + rfm_data['M_Score'].astype(str)
        
        rfm_segment_map = {
            '444': 'Champions',
            '443': 'Loyal',
            '434': 'Loyal',
            '433': 'Loyal',
            '424': 'At Risk',
            '423': 'At Risk',
            '334': 'Need Attention',
            '333': 'Lost',
        }
        
        rfm_data['Segment'] = rfm_data['RFM_Score'].map(rfm_segment_map).fillna('Other')
        
        rfm_summary = rfm_data.groupby('Segment').agg({
            'Customer ID': 'count',
            'Monetary': 'mean',
            'Frequency': 'mean'
        }).sort_values('Monetary', ascending=False)
        
        fig = px.bar(
            rfm_summary,
            title='RFM Segment Summary',
            barmode='group',
            text_auto='.0f'
        )
        fig.update_layout(height=400, **plot_template_config())
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 4: PRODUCT PERFORMANCE ====================
elif page == "📦 Product Performance":
    st.title("📦 Product Performance")
    st.markdown("---")
    
    # Product Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_products = df_filtered['Product ID'].nunique()
        st.markdown(create_kpi_card("Unique Products", unique_products, "number"), unsafe_allow_html=True)
    
    with col2:
        avg_product_profit = df_filtered.groupby('Product ID')['Profit'].sum().mean()
        st.markdown(create_kpi_card("Avg Product Profit", avg_product_profit, "currency"), unsafe_allow_html=True)
    
    with col3:
        profitable_products = (df_filtered.groupby('Product ID')['Profit'].sum() > 0).sum()
        st.markdown(create_kpi_card("Profitable Products", profitable_products, "number"), unsafe_allow_html=True)
    
    with col4:
        loss_products = (df_filtered.groupby('Product ID')['Profit'].sum() < 0).sum()
        st.markdown(create_kpi_card("Loss-Making Products", loss_products, "number"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Product Analysis Tabs
    tab1, tab2, tab3 = st.tabs(["Top Products", "Product Profitability", "Category Deep Dive"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            top_products = df_filtered.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(12)
            
            fig = px.bar(
                x=top_products.values,
                y=top_products.index,
                orientation='h',
                title='Top 12 Products by Sales',
                text_auto='.0f',
                color=top_products.values,
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=450, **plot_template_config(), showlegend=False, yaxis_title="", xaxis_title="Sales ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            top_profit_products = df_filtered.groupby('Product Name')['Profit'].sum().sort_values(ascending=False).head(12)
            
            fig = px.bar(
                x=top_profit_products.values,
                y=top_profit_products.index,
                orientation='h',
                title='Top 12 Products by Profit',
                text_auto='.0f',
                color=top_profit_products.values,
                color_continuous_scale=['#0d1117', '#3fb950']
            )
            fig.update_layout(height=450, **plot_template_config(), showlegend=False, yaxis_title="", xaxis_title="Profit ($)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        product_profit = df_filtered.groupby('Product Name').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum'
        }).sort_values('Profit')
        
        # Bottom loss makers
        bottom_products = product_profit.head(10)
        
        fig = px.bar(
            x=bottom_products['Profit'],
            y=bottom_products.index,
            orientation='h',
            title='Bottom 10 Loss-Making Products',
            text_auto='.0f',
            color=bottom_products['Profit'],
            color_continuous_scale=['#da3633', '#3fb950']
        )
        fig.update_layout(height=400, **plot_template_config(), showlegend=False, xaxis_title="Profit ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Category selection
        selected_category = st.selectbox("Select Category", sorted(df_filtered['Category'].unique()))
        
        category_df = df_filtered[df_filtered['Category'] == selected_category]
        subcategory_perf = category_df.groupby('Sub-Category').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum',
            'Order ID': 'count'
        }).sort_values('Profit', ascending=False)
        
        fig = px.bar(
            subcategory_perf,
            title=f'{selected_category} - Sub-Category Performance',
            barmode='group',
            text_auto='.0f'
        )
        fig.update_layout(height=500, **plot_template_config())
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 5: REGIONAL ANALYSIS ====================
elif page == "🌍 Regional Analysis":
    st.title("🌍 Regional Analysis")
    st.markdown("---")
    
    # Regional Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        unique_states = df_filtered['State'].nunique()
        st.markdown(create_kpi_card("States/Provinces", unique_states, "number"), unsafe_allow_html=True)
    
    with col2:
        unique_cities = df_filtered['City'].nunique()
        st.markdown(create_kpi_card("Cities", unique_cities, "number"), unsafe_allow_html=True)
    
    with col3:
        avg_region_profit = df_filtered.groupby('Region')['Profit'].sum().mean()
        st.markdown(create_kpi_card("Avg Region Profit", avg_region_profit, "currency"), unsafe_allow_html=True)
    
    with col4:
        best_region_profit = df_filtered.groupby('Region')['Profit'].sum().max()
        st.markdown(create_kpi_card("Best Region Profit", best_region_profit, "currency"), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Regional Analysis Tabs
    tab1, tab2, tab3 = st.tabs(["Region Performance", "State Analysis", "Geographic Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            region_data = df_filtered.groupby('Region').agg({
                'Sales': 'sum',
                'Profit': 'sum',
                'Customer ID': 'nunique',
                'Order ID': 'count'
            }).sort_values('Sales', ascending=False)
            
            fig = px.bar(
                region_data,
                title='Region Performance Overview',
                barmode='group',
                text_auto='.0f'
            )
            fig.update_layout(height=400, **plot_template_config())
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            region_profit_ratio = (df_filtered.groupby('Region')['Profit'].sum() / 
                                  df_filtered.groupby('Region')['Sales'].sum() * 100).sort_values(ascending=False)
            
            fig = px.bar(
                x=region_profit_ratio.index,
                y=region_profit_ratio.values,
                title='Profit Ratio by Region',
                text_auto='.1f',
                color=region_profit_ratio.values,
                color_continuous_scale=['#d29922', '#3fb950']
            )
            fig.update_layout(height=400, **plot_template_config(), showlegend=False, yaxis_title="Profit Ratio (%)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Select Region
        selected_region = st.selectbox("Select Region", sorted(df_filtered['Region'].unique()))
        
        region_df = df_filtered[df_filtered['Region'] == selected_region]
        state_perf = region_df.groupby('State').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Customer ID': 'nunique'
        }).sort_values('Sales', ascending=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                state_perf,
                x='Sales',
                y=state_perf.index,
                orientation='h',
                title=f'{selected_region} - Sales by State',
                text_auto='.0f',
                color='Sales',
                color_continuous_scale=['#0d1117', '#58a6ff']
            )
            fig.update_layout(height=500, **plot_template_config(), showlegend=False, xaxis_title="Sales ($)")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.bar(
                state_perf,
                x='Profit',
                y=state_perf.index,
                orientation='h',
                title=f'{selected_region} - Profit by State',
                text_auto='.0f',
                color='Profit',
                color_continuous_scale=['#0d1117', '#3fb950']
            )
            fig.update_layout(height=500, **plot_template_config(), showlegend=False, xaxis_title="Profit ($)")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            region_segment = pd.crosstab(
                df_filtered['Region'],
                df_filtered['Segment'],
                values=df_filtered['Sales'],
                aggfunc='sum'
            )
            
            fig = px.bar(
                region_segment,
                title='Sales by Region & Segment',
                barmode='stack',
                text_auto='.0f'
            )
            fig.update_layout(height=400, **plot_template_config())
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            region_category = pd.crosstab(
                df_filtered['Region'],
                df_filtered['Category'],
                values=df_filtered['Sales'],
                aggfunc='sum'
            )
            
            fig = px.bar(
                region_category,
                title='Sales by Region & Category',
                barmode='stack',
                text_auto='.0f'
            )
            fig.update_layout(height=400, **plot_template_config())
            st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE 6: SALES FORECASTING ====================
elif page == "🤖 Sales Forecasting":
    st.title("🤖 Sales Forecasting")
    st.markdown("---")
    st.write(
        "This section uses historical monthly sales trends and a Random Forest regression model "
        "to forecast future revenue and provide actionable AI-powered sales insights."
    )

    monthly_sales = prepare_monthly_sales(df_filtered)
    if monthly_sales.empty:
        st.warning("No monthly sales data is available for forecasting.")
        st.stop()

    forecast_horizon = st.slider(
        "Forecast Horizon (months)",
        min_value=3,
        max_value=18,
        value=6,
        step=1,
        key="forecast_horizon"
    )

    # Recalculate the forecast every time the slider value changes.
    # This ensures new future indices, new prediction inputs, and a fresh forecast dataframe.
    forecast_horizon = int(forecast_horizon)
    st.write(f"DEBUG: Forecast horizon selected = {forecast_horizon}")

    try:
        model, r2_score, forecast_df = train_random_forest_forecast(
            monthly_sales,
            future_periods=forecast_horizon
        )
        st.write(f"DEBUG: Generated forecast rows = {len(forecast_df)}")
        st.write(f"DEBUG: Future month range = {forecast_df['Month Start'].dt.strftime('%Y-%m').tolist()}")
    except ValueError as exc:
        st.error(str(exc))
        st.stop()

    st.markdown("### Model Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Historical Months", len(monthly_sales))
    col2.metric("Forecast Horizon", f"{forecast_horizon} months")
    col3.metric("Random Forest R²", f"{r2_score:.3f}")

    combined_df = pd.concat(
        [monthly_sales[['Month Start', 'Sales']].assign(Type='Actual'),
         forecast_df[['Month Start', 'Sales']].assign(Type='Forecast')],
        ignore_index=True
    )

    forecast_tabs = st.tabs(["Trend Chart", "Forecast Table"])
    with forecast_tabs[0]:
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=monthly_sales['Month Start'],
                y=monthly_sales['Sales'],
                mode='lines+markers',
                name='Actual Sales',
                line=dict(color='#58a6ff', width=3),
                marker=dict(size=6)
            )
        )
        fig.add_trace(
            go.Scatter(
                x=forecast_df['Month Start'],
                y=forecast_df['Sales'],
                mode='lines+markers',
                name='Forecast Sales',
                line=dict(color='#ff7b72', width=3, dash='dash'),
                marker=dict(size=6)
            )
        )
        fig.update_layout(
            title='Actual vs Predicted Monthly Sales Trend',
            xaxis_title='Month',
            yaxis_title='Sales ($)',
            legend=dict(bgcolor='#0e1117', bordercolor='#30363d', borderwidth=1),
            height=520,
            **plot_template_config()
        )
        st.plotly_chart(fig, use_container_width=True)

    with forecast_tabs[1]:
        st.markdown("### Forecast Output")
        st.dataframe(
            forecast_df.rename(columns={
                'Month Start': 'Month',
                'Sales': 'Predicted Sales'
            }).assign(**{
                'Month': lambda df: df['Month'].dt.strftime('%Y-%m')
            }),
            use_container_width=True
        )

    st.markdown(
        "---\n"
        "The forecasting model is trained on monthly historical sales data. "
        "Future sales are predicted using an ensemble Random Forest model built into this AI-powered dashboard."
    )

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #8b949e; font-size: 0.9rem; padding: 2rem;">
        <p>📊 <strong>E-Commerce Sales & Customer Analytics Dashboard</strong></p>
        <p>Professional Business Intelligence Platform | Powered by Streamlit & Plotly</p>
        <p>Last Updated: """ + datetime.now().strftime("%B %d, %Y at %I:%M %p") + """</p>
    </div>
    """,
    unsafe_allow_html=True
)
