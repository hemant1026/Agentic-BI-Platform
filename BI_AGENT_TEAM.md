# BI Agent Team - Deep Data Analysis System

## Overview
The BI Agent Team is a multi-agent system that performs deep analysis of data to generate meaningful KPIs, visualizations, and insights. It ensures no false information is presented and all visualizations are properly named and contextualized.

## Architecture

### 1. Data Structure Agent
- **Purpose**: Understands data structure and infers column meanings
- **Capabilities**:
  - Detects data types (numeric, categorical, temporal, etc.)
  - Infers column meanings from data patterns
  - Analyzes data quality (null counts, uniqueness, etc.)
  - Identifies relationships between columns

### 2. Visualization Agent
- **Purpose**: Recommends appropriate visualizations based on data structure
- **Capabilities**:
  - Selects chart types based on data characteristics
  - Generates meaningful titles using column metadata
  - Prioritizes visualizations by importance
  - Handles both summary/report formats and standard tabular data

### 3. KPI Agent
- **Purpose**: Generates meaningful KPIs with proper context
- **Capabilities**:
  - Calculates statistical metrics (mean, median, std, etc.)
  - Provides context-specific metrics (totals for financial data, counts for categorical)
  - Generates human-readable KPI names
  - Ensures accuracy and prevents false information

## Smart Data Parser

The system includes a smart parser that handles complex Excel structures:

### Summary/Report Format Detection
- Detects label-value pair structures
- Identifies section headers
- Transforms summary data into structured format
- Infers column meanings from labels and values

### Column Name Inference
- Analyzes data patterns to infer meaning
- Maps generic column names (e.g., "Unnamed: 1") to meaningful names
- Examples:
  - Sales/Revenue data → "Sales Amount"
  - Tax data → "Tax Amount"
  - Tips/Gratuity → "Tips/Gratuity"
  - Counts → "Count"
  - Averages → "Average"

## Visualization Naming

All visualizations receive meaningful titles:
- **Bar Charts**: "{Metric Name} by Category"
- **Histograms**: "Distribution of {Metric Name}"
- **Scatter Plots**: "{X Metric} vs {Y Metric}"
- **Heatmaps**: "Correlation Matrix"

## Data Validation

The system ensures accuracy by:
1. **Type Checking**: Validates data types before calculations
2. **Null Handling**: Properly handles missing data
3. **Range Validation**: Checks for outliers and anomalies
4. **Context Awareness**: Uses data context to prevent misinterpretation

## Usage

The BI Agent Team is automatically invoked when uploading data through the API:

```javascript
POST /api/upload
- File is analyzed by smart parser
- BI Agent Team generates KPIs and visualizations
- Results include enhanced metadata and meaningful names
```

## Output Format

```json
{
  "data": [...],
  "columns": [...],
  "column_metadata": [
    {
      "original": "Unnamed: 1",
      "clean": "Column_1",
      "display_name": "Sales Amount",
      "type": "numeric"
    }
  ],
  "kpis": {
    "Sales Amount": {
      "mean": 1234.56,
      "median": 1000.00,
      "min": 0,
      "max": 5000,
      "display_name": "Sales Amount"
    }
  },
  "visualizations": [
    {
      "type": "bar",
      "title": "Sales Amount by Category",
      "xColumn": "Label",
      "yColumn": "Column_1"
    }
  ]
}
```

## Benefits

1. **No False Information**: All calculations are validated and contextualized
2. **Meaningful Names**: Generic column names are replaced with descriptive ones
3. **Proper Context**: Visualizations are chosen based on data characteristics
4. **Deep Analysis**: Multi-agent approach ensures comprehensive understanding
5. **Flexible**: Handles both standard tables and complex report formats

