# Example Datasets

Sample datasets for testing the Agentic BI Platform. Upload any of these through the UI at http://localhost:3002.

| Dataset | Rows | Columns | Domain | Description |
|---------|------|---------|--------|-------------|
| `sample_data.csv` | 20 | 6 | Retail | Daily sales by region and product category. Good for time series, bar charts, and scatter plots. |
| `ecommerce_orders.csv` | 100 | 13 | E-commerce | Order history with products, categories, payment methods, shipping, and discounts. Tests multi-column KPI generation. |
| `employee_performance.csv` | 50 | 12 | HR | Employee metrics including performance scores, satisfaction, salary, training, and overtime. Tests distribution analysis and correlation detection. |
| `financial_quarterly.csv` | 24 | 12 | Finance | 6 years of quarterly P&L data with revenue, costs, profit, assets, liabilities, and headcount. Tests trend detection and financial KPIs. |

## Programmatic Usage

```bash
# Analyze a single file
python examples/quick_analysis.py data/sample_data.csv

# Batch analyze all datasets
python examples/batch_analysis.py data/
```
