#!/usr/bin/env python3
"""
Get chart data for a specific visualization
"""
import sys
import json
import pandas as pd
import numpy as np

def get_chart_data(file_path, chart_type, x_column, y_column):
    try:
        # Load data - use same logic as process_data.py
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            # Use same Excel reading logic as process_data.py
            try:
                df = pd.read_excel(file_path, header=0)
                if any('Unnamed' in str(col) for col in df.columns):
                    df_temp = pd.read_excel(file_path, header=None)
                    header_row = 0
                    max_non_null = 0
                    for idx in range(min(10, len(df_temp))):
                        non_null_count = df_temp.iloc[idx].notna().sum()
                        if non_null_count > max_non_null:
                            max_non_null = non_null_count
                            header_row = idx
                    df = pd.read_excel(file_path, header=header_row)
                df.columns = [str(col).strip() if pd.notna(col) and str(col) != 'nan' else f'Column_{i}' 
                             for i, col in enumerate(df.columns)]
                df = df.dropna(how='all').dropna(axis=1, how='all')
            except:
                df = pd.read_excel(file_path)
                df = df.dropna(how='all').dropna(axis=1, how='all')
        
        result = {
            'chartType': chart_type,
            'xColumn': x_column,
            'yColumn': y_column
        }
        
        if chart_type == 'histogram' and x_column and x_column in df.columns:
            # Convert to numeric if needed
            values = pd.to_numeric(df[x_column], errors='coerce').dropna().tolist()
            if len(values) > 0:
                result['data'] = {
                    'x': values,
                    'type': 'histogram'
                }
            else:
                result['error'] = f'Column {x_column} has no numeric data'
        elif chart_type == 'bar' and x_column and x_column in df.columns:
            # Check if y_column is provided and valid
            if y_column and y_column.strip() and y_column in df.columns:
                # Bar chart with x and y
                x_data = df[x_column].dropna().tolist()
                y_data = pd.to_numeric(df[y_column], errors='coerce').dropna().tolist()
                if len(x_data) > 0 and len(y_data) > 0:
                    result['data'] = {
                        'x': x_data[:len(y_data)],
                        'y': y_data[:len(x_data)],
                        'type': 'bar'
                    }
                else:
                    result['error'] = 'No valid data for bar chart'
            else:
                # Frequency bar chart (no y column)
                data_col = df[matching_col].dropna()
                if len(data_col) > 0:
                    value_counts = data_col.value_counts().head(20)
                    if len(value_counts) > 0:
                        result['data'] = {
                            'x': [str(x) for x in value_counts.index.tolist()],
                            'y': value_counts.values.tolist(),
                            'type': 'bar'
                        }
                    else:
                        result['error'] = f'Column {x_column} has no valid values for frequency chart'
                else:
                    result['error'] = f'Column {x_column} has no data'
        elif chart_type == 'scatter' and x_column and y_column and x_column in df.columns and y_column in df.columns:
            x_data = pd.to_numeric(df[x_column], errors='coerce').dropna()
            y_data = pd.to_numeric(df[y_column], errors='coerce').dropna()
            if len(x_data) > 0 and len(y_data) > 0:
                # Align data by index
                common_idx = x_data.index.intersection(y_data.index)
                result['data'] = {
                    'x': x_data.loc[common_idx].tolist(),
                    'y': y_data.loc[common_idx].tolist(),
                    'type': 'scatter',
                    'mode': 'markers'
                }
            else:
                result['error'] = 'No valid numeric data for scatter plot'
        elif chart_type == 'line' and x_column and y_column and x_column in df.columns and y_column in df.columns:
            # Sort by x column for line charts
            try:
                df_sorted = df.sort_values(by=x_column)
                x_data = df_sorted[x_column].dropna().tolist()
                y_data = pd.to_numeric(df_sorted[y_column], errors='coerce').dropna().tolist()
                if len(x_data) > 0 and len(y_data) > 0:
                    result['data'] = {
                        'x': x_data[:len(y_data)],
                        'y': y_data[:len(x_data)],
                        'type': 'scatter',
                        'mode': 'lines+markers'
                    }
                else:
                    result['error'] = 'No valid data for line chart'
            except:
                result['error'] = 'Could not sort data for line chart'
        elif chart_type == 'heatmap':
            numeric_df = df.select_dtypes(include=[np.number])
            if len(numeric_df.columns) > 1:
                corr = numeric_df.corr()
                result['data'] = {
                    'z': corr.values.tolist(),
                    'x': corr.columns.tolist(),
                    'y': corr.columns.tolist(),
                    'type': 'heatmap'
                }
            else:
                result['error'] = 'Not enough numeric columns for heatmap'
        
        # If no data was set and no error, set a default error
        if 'data' not in result and 'error' not in result:
            result['error'] = f'Could not generate chart data for type {chart_type} with columns {x_column}, {y_column}'
        
        print(json.dumps(result))
        return result
        
    except Exception as e:
        error_result = {'error': str(e)}
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({'error': 'Missing arguments'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    chart_type = sys.argv[2]
    x_column = sys.argv[3]
    y_column = sys.argv[4] if len(sys.argv) > 4 else ''
    get_chart_data(file_path, chart_type, x_column, y_column)

