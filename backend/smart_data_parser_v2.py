#!/usr/bin/env python3
"""
Smart data parser v2 - Simplified and robust
Creates meaningful column names based on actual data analysis
"""
import sys
import json
import pandas as pd
import numpy as np

def parse_sales_summary_format(file_path: str) -> dict:
    """Parse sales summary format and create meaningful column names"""
    try:
        df_raw = pd.read_excel(file_path, header=None)
        
        # Collect data rows
        data_rows = []
        current_section = None
        
        for idx, row in df_raw.iterrows():
            first_col = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            
            if not first_col or first_col == 'nan':
                continue
            
            # Detect section headers
            if first_col.endswith('summary') or first_col.endswith('Summary'):
                current_section = first_col
                continue
            
            # Find numeric values in this row
            row_values = {}
            for col_idx in range(1, len(row)):
                val = row.iloc[col_idx]
                if pd.notna(val):
                    try:
                        float_val = float(val)
                        row_values[col_idx] = float_val
                    except:
                        pass
            
            if row_values:
                data_rows.append({
                    'label': first_col,
                    'section': current_section or 'Main',
                    'values': row_values
                })
        
        # Build dataframe
        all_col_indices = set()
        for row in data_rows:
            all_col_indices.update(row['values'].keys())
        all_col_indices = sorted(list(all_col_indices))
        
        # Create column name mapping based on what labels appear in each column
        column_names = {}
        for col_idx in all_col_indices:
            labels_in_col = []
            values_in_col = []
            for row in data_rows:
                if col_idx in row['values']:
                    labels_in_col.append(row['label'])
                    values_in_col.append(row['values'][col_idx])
            
            # Analyze to create meaningful name
            labels_str = ' '.join([str(l).lower() for l in labels_in_col[:10]])
            max_val = max(values_in_col) if values_in_col else 0
            
            # Determine column name based on content
            if col_idx == 1:
                if any(word in labels_str for word in ['net sales', 'total', 'gratuity', 'tax', 'tips']):
                    column_names[col_idx] = 'Total Revenue'
                else:
                    column_names[col_idx] = 'Primary Sales'
            elif col_idx == 2:
                if any(word in labels_str for word in ['service mode', 'total guests', 'avg/guest']):
                    column_names[col_idx] = 'Service Mode Sales'
                else:
                    column_names[col_idx] = 'Secondary Sales'
            elif col_idx == 3:
                if any(word in labels_str for word in ['service mode', 'net sales']):
                    column_names[col_idx] = 'Service Mode Sales 2'
                else:
                    column_names[col_idx] = 'Tertiary Sales'
            elif col_idx == 4:
                if any(word in labels_str for word in ['payment type', 'cash', 'credit', 'debit']):
                    column_names[col_idx] = 'Payment Type Amount'
                else:
                    column_names[col_idx] = 'Payment Breakdown 1'
            elif col_idx == 5:
                if any(word in labels_str for word in ['payment type', 'cash', 'credit']):
                    column_names[col_idx] = 'Payment Type Amount 2'
                else:
                    column_names[col_idx] = 'Payment Breakdown 2'
            else:
                # Generic naming for other columns
                if max_val > 5000:
                    column_names[col_idx] = f'Total Amount Column {col_idx}'
                elif max_val > 1000:
                    column_names[col_idx] = f'Sales Amount Column {col_idx}'
                elif max_val < 200:
                    column_names[col_idx] = f'Count Column {col_idx}'
                else:
                    column_names[col_idx] = f'Amount Column {col_idx}'
        
        # Build structured data with meaningful column names
        structured_data = []
        for row in data_rows:
            record = {'Label': row['label'], 'Section': row['section']}
            for col_idx in all_col_indices:
                col_name = column_names.get(col_idx, f'Column_{col_idx}')
                record[col_name] = row['values'].get(col_idx, None)
            structured_data.append(record)
        
        df = pd.DataFrame(structured_data)
        
        # Identify numeric columns
        numeric_columns = []
        categorical_columns = ['Label', 'Section']
        
        for col in df.columns:
            if col not in ['Label', 'Section']:
                converted = pd.to_numeric(df[col], errors='coerce')
                if converted.notna().sum() > len(df) * 0.3:
                    df[col] = converted
                    numeric_columns.append(col)
                else:
                    categorical_columns.append(col)
        
        # Create column metadata
        column_metadata = []
        for col in numeric_columns:
            values = df[col].dropna()
            if len(values) > 0:
                column_metadata.append({
                    'original': col,
                    'clean': col,
                    'display_name': col,  # Already meaningful
                    'type': 'numeric',
                    'description': f'Sales data: {col}'
                })
        
        result = {
            'data': df.replace({np.nan: None}).to_dict('records'),
            'columns': df.columns.tolist(),
            'column_metadata': column_metadata,
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0]),
            'format': 'summary_report'
        }
        
        print(json.dumps(result), file=sys.stdout)
        sys.stdout.flush()
        return result
        
    except Exception as e:
        error_result = {'error': str(e)}
        print(json.dumps(error_result), file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing file path'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    parse_sales_summary_format(file_path)

