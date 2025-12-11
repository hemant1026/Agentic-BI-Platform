#!/usr/bin/env python3
"""
Process uploaded data file and return structured information
Supports multiple file formats with automatic detection
"""
import sys
import json
import pandas as pd
import numpy as np
import os

def process_file(file_path, dataset_name):
    try:
        df = None
        file_ext = os.path.splitext(file_path)[1].lower() if '.' in file_path else ''
        
        # Try multiple strategies to load the file
        strategies = []
        
        # Strategy 1: Based on file extension (prioritize these)
        if file_ext == '.csv':
            strategies.append(('CSV', lambda: pd.read_csv(file_path)))
        elif file_ext == '.json':
            strategies.append(('JSON', lambda: pd.read_json(file_path)))
        elif file_ext in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
            strategies.append(('Excel', lambda: pd.read_excel(file_path)))
        elif file_ext == '.tsv':
            strategies.append(('TSV', lambda: pd.read_csv(file_path, sep='\t')))
        elif file_ext == '.txt':
            # Try as CSV first, then TSV
            strategies.append(('TXT as CSV', lambda: pd.read_csv(file_path)))
            strategies.append(('TXT as TSV', lambda: pd.read_csv(file_path, sep='\t')))
        
        # Strategy 2: Try Excel with advanced parsing (for any file, including Excel)
        if file_ext in ['.xlsx', '.xls', '.xlsm', '.xlsb'] or True:
            def try_excel_advanced():
                # Try reading with first row as header
                df_temp = pd.read_excel(file_path, header=0)
                
                # If we get unnamed columns, try to find the actual header
                if any('Unnamed' in str(col) for col in df_temp.columns):
                    # Try reading without header and find the header row
                    df_check = pd.read_excel(file_path, header=None)
                    
                    # Find row with most non-null values (likely header)
                    header_row = 0
                    max_non_null = 0
                    for idx in range(min(10, len(df_check))):
                        non_null_count = df_check.iloc[idx].notna().sum()
                        if non_null_count > max_non_null:
                            max_non_null = non_null_count
                            header_row = idx
                    
                    # Read with found header row
                    df_temp = pd.read_excel(file_path, header=header_row)
                
                # Clean column names
                df_temp.columns = [str(col).strip() if pd.notna(col) and str(col) != 'nan' else f'Column_{i}' 
                                 for i, col in enumerate(df_temp.columns)]
                
                # Remove rows where all values are null
                df_temp = df_temp.dropna(how='all')
                
                # Remove columns where all values are null
                df_temp = df_temp.dropna(axis=1, how='all')
                
                # Remove rows that are mostly empty
                df_temp = df_temp[df_temp.notna().sum(axis=1) > 1]
                
                # If we have very few rows, the file might be a summary format
                # Try to transpose if it looks like a summary
                if len(df_temp) < 5 and len(df_temp.columns) > len(df_temp):
                    try:
                        df_alt = pd.read_excel(file_path, header=None)
                        if df_alt.shape[0] > df_alt.shape[1]:
                            df_alt = df_alt.T
                            if len(df_alt) > 0:
                                df_alt.columns = df_alt.iloc[0]
                                df_alt = df_alt.iloc[1:].reset_index(drop=True)
                                df_alt = df_alt.dropna(how='all').dropna(axis=1, how='all')
                                if len(df_alt) > len(df_temp):
                                    df_temp = df_alt
                    except:
                        pass
                
                return df_temp
            
            strategies.append(('Excel Advanced', try_excel_advanced))
        
        # Strategy 3: Try common formats (for files without extension or unknown extensions)
        # Try CSV (comma-separated)
        strategies.append(('Auto CSV', lambda: pd.read_csv(file_path)))
        # Try TSV (tab-separated)
        strategies.append(('Auto TSV', lambda: pd.read_csv(file_path, sep='\t')))
        # Try JSON
        strategies.append(('Auto JSON', lambda: pd.read_json(file_path)))
        # Try Excel as last resort
        strategies.append(('Auto Excel', lambda: pd.read_excel(file_path)))
        
        # Try each strategy until one works
        last_error = None
        for strategy_name, strategy_func in strategies:
            try:
                df = strategy_func()
                if df is not None and not df.empty:
                    print(f"Successfully loaded using: {strategy_name}", file=sys.stderr)
                    break
            except Exception as e:
                last_error = str(e)
                continue
        
        # Check if df was loaded successfully
        if df is None or df.empty:
            error_msg = f"Failed to load data. Tried multiple formats. Last error: {last_error}" if last_error else "Failed to load data or file is empty"
            raise ValueError(error_msg)
        
        # Identify column types - try to convert object columns to numeric
        # First, try converting object columns that might contain numbers
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    # Try to convert to numeric
                    converted = pd.to_numeric(df[col], errors='coerce')
                    # If at least 50% of non-null values are numeric, convert the column
                    non_null_count = df[col].notna().sum()
                    numeric_count = converted.notna().sum()
                    if non_null_count > 0 and numeric_count / non_null_count > 0.5:
                        df[col] = converted
                        print(f"Converted column '{col}' to numeric ({numeric_count}/{non_null_count} values)", file=sys.stderr)
                except:
                    pass
        
        # Now identify column types
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_columns = df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        # Filter out columns that are all NaN
        numeric_columns = [col for col in numeric_columns if df[col].notna().sum() > 0]
        categorical_columns = [col for col in categorical_columns if df[col].notna().sum() > 0]
        
        # Convert to JSON-serializable format
        # For large datasets, sample the data
        max_rows = 10000
        if len(df) > max_rows:
            df_sample = df.head(max_rows)
        else:
            df_sample = df
        
        # Convert to records
        data = df_sample.replace({np.nan: None}).to_dict('records')
        
        result = {
            'data': data,
            'columns': df.columns.tolist(),
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0])
        }
        
        print(json.dumps(result))
        return result
        
    except Exception as e:
        error_result = {'error': str(e)}
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Missing arguments'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    dataset_name = sys.argv[2]
    process_file(file_path, dataset_name)
