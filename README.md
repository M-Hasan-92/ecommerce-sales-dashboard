# E-Commerce Sales & Customer Analytics Dashboard

A professional, enterprise-grade analytics dashboard built with **Streamlit** and **Plotly** for analyzing e-commerce sales data. This dashboard provides comprehensive business intelligence across multiple dimensions including sales performance, customer behavior, product analysis, and regional insights.

---

## 🎯 Features

### 📊 Business Overview
- Real-time KPI tracking (Total Sales, Profit, Orders, Profit Ratio)
- Monthly sales and profit trend analysis
- Category and segment distribution
- Delta metrics showing period-over-period changes

### 💰 Sales Analysis
- Sales breakdown by category, region, and sub-category
- Ship mode analysis
- Discount impact analysis showing correlation between discounts and profitability
- Average order value and unit metrics

### 👥 Customer Insights
- Customer lifetime value analysis
- Segment performance comparison (Consumer, Corporate, Home Office)
- Top customer identification
- RFM (Recency, Frequency, Monetary) customer segmentation
- Repeat customer tracking

### 📦 Product Performance
- Top performing products by sales and profit
- Loss-making product identification
- Product profitability analysis
- Category deep-dive with sub-category performance

### 🌍 Regional Analysis
- Region-wise performance metrics
- State-level sales and profit analysis
- Cross-tabulation analysis (Region × Segment, Region × Category)
- Geographic customer distribution

---

## 🎨 Design Philosophy

The dashboard follows modern SaaS design principles:
- **Dark Theme**: Professional dark UI similar to Netflix, GitHub, and enterprise analytics tools
- **Minimal Color Palette**: Primary blue (#58a6ff), success green (#3fb950), warning amber (#d29922)
- **Clean Typography**: System fonts with proper hierarchy
- **Responsive Layout**: Optimized for 1920x1080 and larger screens
- **Interactive Visualizations**: Hover details, clickable elements, and smooth animations

---

## 🛠️ Technology Stack

| Technology | Purpose |
|-----------|---------|
| **Streamlit** | Web framework for interactive dashboards |
| **Pandas** | Data manipulation and analysis |
| **NumPy** | Numerical computations |
| **Plotly** | Interactive data visualizations |
| **Python** | Core programming language |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd "E-commerce sales prediction dashboard"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows
   # or
   source venv/bin/activate      # On macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure the dataset is in the project directory:**
   ```
   superstore.csv
   ```

---

## 🚀 Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open in your default browser at `http://localhost:8501`

---

## 📖 Dashboard Navigation

### Sidebar Controls
- **Navigation Menu**: 5 main views accessible from the left sidebar
- **Filters**: 
  - Date Range: Filter data by custom time periods
  - Region: Select one or multiple regions
  - Category: Filter by product category
  - Segment: Choose customer segments
  - Ship Mode: Filter by shipping method

### Main Views

#### 1. Business Overview
Start here for high-level metrics and trends.
- KPI cards for quick reference
- Monthly sales and profit trends
- Category and segment distribution

#### 2. Sales Analysis
Detailed sales performance metrics.
- Tabbed interface for Category, Region, Sub-Category, and Ship Mode analysis
- Discount vs. Profit correlation
- Top and bottom performers

#### 3. Customer Insights
Understand customer behavior and segments.
- Top customers by sales and profit
- Segment performance metrics
- Customer distribution analysis
- RFM customer segmentation

#### 4. Product Performance
Product-level analytics.
- Top performing products
- Loss-making product identification
- Category deep-dive analysis

#### 5. Regional Analysis
Geographic performance insights.
- Region performance overview
- State-level analysis
- Cross-tabulation insights

---

## 📊 Dataset Information

The dashboard uses the **Superstore** dataset with the following structure:

### Key Columns
- **Order Information**: Order ID, Order Date, Ship Date, Ship Mode
- **Customer Data**: Customer ID, Customer Name, Segment
- **Geographic**: Region, State, City, Postal Code, Country
- **Product**: Product ID, Product Name, Category, Sub-Category
- **Metrics**: Sales, Quantity, Discount, Profit

### Data Processing
The app automatically:
- Converts date columns to datetime format
- Calculates additional metrics (Days to Ship, Profit Ratio, Year, Month, Quarter)
- Removes duplicate rows
- Handles missing values
- Caches data for performance

---

## 🎯 Key Calculations

### Profit Ratio
```
Profit Ratio (%) = (Profit / Sales) × 100
```

### Average Order Value
```
Average Order Value = Total Sales / Total Unique Orders
```

### Days to Ship
```
Days to Ship = Ship Date - Order Date
```

### RFM Segmentation
- **Recency**: Days since last purchase
- **Frequency**: Number of orders by customer
- **Monetary**: Total spent by customer

---

## 🎨 Color Scheme

The dashboard uses a professional color palette:

| Color | Hex Code | Usage |
|-------|----------|-------|
| Blue | #58a6ff | Primary metrics, sales data |
| Green | #3fb950 | Profit, success metrics |
| Amber | #d29922 | Warning, moderate metrics |
| Dark Background | #0e1117 | Main background |
| Card Background | #161b22 | Component backgrounds |
| Border | #30363d | Dividers and borders |
| Text | #c9d1d9 | Primary text color |
| Muted Text | #8b949e | Secondary text |

---

## ⚡ Performance Optimization

- **Data Caching**: Uses Streamlit's @st.cache_data decorator to cache data loading and cleaning operations
- **Lazy Loading**: Visualizations are generated on-demand
- **Efficient Filtering**: Filters applied at data level before visualization
- **Optimized Queries**: Grouped operations with minimal data duplication

---

## 🔧 Customization

### Modifying Filters
Edit the sidebar filter section in `app.py`:
```python
regions = st.multiselect("Select Region(s)", ...)
```

### Changing Colors
Update the color codes in the template configuration:
```python
marker_colors=['#58a6ff', '#3fb950', '#d29922']
```

### Adding New Metrics
Add new KPI cards in any page:
```python
st.markdown(create_kpi_card("Metric Name", value, "metric_type"), unsafe_allow_html=True)
```

---

## 📈 Use Cases

This dashboard is ideal for:
- **Business Analysts**: Monitor KPIs and identify trends
- **Sales Teams**: Track sales performance and customer metrics
- **Operations**: Analyze shipping modes and logistics efficiency
- **Marketing**: Understand customer segments and behavior
- **Finance**: Monitor profitability and discount impact
- **Executives**: Review high-level business metrics

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution**: Install requirements:
```bash
pip install -r requirements.txt
```

### Issue: "FileNotFoundError" for CSV file
**Solution**: Ensure `superstore.csv` is in the same directory as `app.py`

### Issue: Dashboard loads slowly
**Solution**: 
- Clear browser cache
- Restart the Streamlit server
- Check internet connection for large datasets

### Issue: Charts not displaying
**Solution**: 
- Verify Plotly is installed: `pip install --upgrade plotly`
- Check for data filtering that might result in empty datasets

---

## 📝 File Structure

```
E-commerce sales prediction dashboard/
├── app.py                          # Main dashboard application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── PROJECT_DESCRIPTION.md          # Detailed project documentation
└── superstore.csv         # Dataset (provided)
```

---

## 🚀 Deployment

### Local Deployment
```bash
streamlit run app.py
```

### Cloud Deployment (Streamlit Cloud)
1. Push code to GitHub repository
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Deploy in one click

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app.py"]
```

---

## 📊 Sample Insights

The dashboard can help answer questions like:
- Which regions generate the most revenue?
- What is the relationship between discounts and profitability?
- Who are our top customers?
- Which products are loss-making?
- How do customer segments differ?
- What is the optimal shipping method by region?

---

## 📞 Support & Documentation

For more information:
- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

---

## 📄 License

This project is provided as-is for business intelligence and analytics purposes.

---

## ✨ Version History

**v1.0.0** (2024)
- Initial release
- 5 main dashboard views
- 15+ interactive visualizations
- Advanced filtering capabilities
- RFM customer segmentation
- Professional dark theme

---

**Created with ❤️ for data-driven decision making**
