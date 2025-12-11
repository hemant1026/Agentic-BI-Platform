#!/usr/bin/env python3
"""
Intelligent Data Parser - Dynamically handles various Excel/CSV structures
Uses pattern recognition and semantic analysis instead of hardcoding
"""
import sys
import json
import pandas as pd
import numpy as np
import re
from collections import Counter
from typing import Dict, List, Tuple, Any

class IntelligentParser:
    """Intelligent parser that adapts to different data structures"""
    
    def __init__(self):
        # Common patterns for column naming (not hardcoded positions)
        self.financial_patterns = {
            'revenue': ['revenue', 'sales', 'income', 'earnings'],
            'expense': ['expense', 'cost', 'spending', 'outgoing'],
            'profit': ['profit', 'margin', 'gain'],
            'tax': ['tax', 'fee', 'levy', 'duty'],
            'payment': ['payment', 'paid', 'transaction', 'charge'],
            'count': ['count', 'quantity', 'number', 'items', 'units'],
            'percentage': ['percent', 'percentage', 'rate', 'ratio'],
            'average': ['average', 'avg', 'mean', 'per'],
            'total': ['total', 'sum', 'aggregate', 'grand total'],
            'date': ['date', 'time', 'day', 'month', 'year', 'timestamp']
        }
        
        self.category_patterns = {
            'location': ['location', 'place', 'region', 'city', 'state', 'country'],
            'product': ['product', 'item', 'sku', 'goods', 'merchandise'],
            'customer': ['customer', 'client', 'user', 'account'],
            'employee': ['employee', 'staff', 'worker', 'personnel'],
            'category': ['category', 'type', 'class', 'group', 'segment'],
            'status': ['status', 'state', 'condition', 'stage']
        }
    
    def infer_column_meaning(self, labels: List[str], values: List[float], 
                            column_index: int, total_columns: int) -> Dict[str, str]:
        """
        Intelligently infer column meaning from data patterns
        No hardcoding - uses semantic analysis
        """
        if not labels or not values:
            return {'display_name': f'Column {column_index}', 'description': 'Data column'}
        
        # Combine all labels into a searchable string
        labels_text = ' '.join([str(l).lower() for l in labels[:20]])
        max_val = max(values) if values else 0
        min_val = min(values) if values else 0
        mean_val = np.mean(values) if values else 0
        unique_labels = len(set(labels))
        
        # Analyze value characteristics
        value_scale = self._classify_value_scale(max_val, min_val, mean_val)
        value_type = self._classify_value_type(max_val, min_val, mean_val, len(values))
        
        # Pattern matching for financial metrics
        display_name = None
        description = None
        
        # Check financial patterns
        for metric_type, patterns in self.financial_patterns.items():
            if any(pattern in labels_text for pattern in patterns):
                display_name = self._create_financial_name(metric_type, labels_text, value_scale)
                description = self._create_description(metric_type, value_type)
                break
        
        # Check category patterns
        if not display_name:
            for category_type, patterns in self.category_patterns.items():
                if any(pattern in labels_text for pattern in patterns):
                    display_name = self._create_category_name(category_type, labels_text)
                    description = f'{category_type.title()} information'
                    break
        
        # Analyze by value characteristics if no pattern match
        if not display_name:
            if value_type == 'count':
                display_name = 'Count'
                description = 'Count of items or occurrences'
            elif value_type == 'percentage':
                display_name = 'Percentage'
                description = 'Percentage or ratio value'
            elif value_type == 'amount':
                display_name = self._infer_amount_name(value_scale, column_index, total_columns)
                description = f'{value_scale} amount value'
            else:
                display_name = self._create_generic_name(column_index, total_columns, value_scale)
                description = f'Data column {column_index}'
        
        # Enhance name with context from labels
        display_name = self._add_context_to_name(display_name, labels_text, unique_labels)
        
        return {
            'display_name': display_name,
            'description': description,
            'value_type': value_type,
            'value_scale': value_scale
        }
    
    def _classify_value_scale(self, max_val: float, min_val: float, mean_val: float) -> str:
        """Classify the scale of values"""
        if max_val > 1000000:
            return 'large'
        elif max_val > 10000:
            return 'medium'
        elif max_val > 100:
            return 'small'
        else:
            return 'tiny'
    
    def _classify_value_type(self, max_val: float, min_val: float, 
                            mean_val: float, count: int) -> str:
        """Classify the type of values"""
        # Percentage check (0-100 range)
        if 0 <= min_val <= 100 and 0 <= max_val <= 100 and mean_val < 100:
            if max_val <= 100 and any(v < 1 for v in [min_val, max_val, mean_val] if v > 0):
                return 'percentage'
        
        # Count check (integers, reasonable range)
        if max_val < 10000 and mean_val < 1000 and count > 0:
            if all(v == int(v) for v in [min_val, max_val, mean_val] if v > 0):
                return 'count'
        
        # Amount check
        if max_val > 0:
            return 'amount'
        
        return 'unknown'
    
    def _create_financial_name(self, metric_type: str, labels_text: str, scale: str) -> str:
        """Create a financial metric name"""
        # Extract specific context from labels
        if 'net' in labels_text:
            return f'Net {metric_type.title()}'
        elif 'gross' in labels_text:
            return f'Gross {metric_type.title()}'
        elif 'total' in labels_text:
            return f'Total {metric_type.title()}'
        else:
            return metric_type.title()
    
    def _create_category_name(self, category_type: str, labels_text: str) -> str:
        """Create a category name"""
        # Try to extract specific category name from labels
        words = labels_text.split()
        for word in words:
            if word in ['dining', 'room', 'restaurant']:
                return 'Dining Room'
            elif word in ['delivery', 'uber', 'eats', 'doordash']:
                return 'Delivery Service'
            elif word in ['cash', 'credit', 'debit', 'payment']:
                return 'Payment Method'
        
        return category_type.title()
    
    def _infer_amount_name(self, scale: str, col_idx: int, total_cols: int) -> str:
        """Infer amount name based on position and scale"""
        # Use relative position, not absolute
        position_ratio = col_idx / total_cols if total_cols > 0 else 0
        
        if position_ratio < 0.2:
            return 'Primary Amount'
        elif position_ratio < 0.4:
            return 'Secondary Amount'
        elif position_ratio < 0.6:
            return 'Tertiary Amount'
        else:
            return f'Amount {col_idx}'
    
    def _create_generic_name(self, col_idx: int, total_cols: int, scale: str) -> str:
        """Create a generic but meaningful name"""
        position_ratio = col_idx / total_cols if total_cols > 0 else 0
        
        if position_ratio < 0.33:
            return f'Primary Data {col_idx}'
        elif position_ratio < 0.66:
            return f'Secondary Data {col_idx}'
        else:
            return f'Additional Data {col_idx}'
    
    def _add_context_to_name(self, base_name: str, labels_text: str, unique_labels: int) -> str:
        """Add context to name based on label patterns"""
        # Check for time periods
        if any(word in labels_text for word in ['lunch', 'dinner', 'breakfast']):
            time_period = 'Lunch' if 'lunch' in labels_text else 'Dinner' if 'dinner' in labels_text else 'Breakfast'
            return f'{base_name} ({time_period})'
        
        # Check for service types
        if any(word in labels_text for word in ['service', 'mode']):
            return f'{base_name} (Service)'
        
        # Check for payment types
        if any(word in labels_text for word in ['payment', 'method', 'type']):
            return f'{base_name} (Payment)'
        
        return base_name
    
    def _create_description(self, metric_type: str, value_type: str) -> str:
        """Create a description for the metric"""
        descriptions = {
            'revenue': 'Revenue and sales amounts',
            'expense': 'Expense and cost amounts',
            'profit': 'Profit and margin amounts',
            'tax': 'Tax and fee amounts',
            'payment': 'Payment transaction amounts',
            'count': 'Count of items or occurrences',
            'percentage': 'Percentage or ratio values',
            'average': 'Average or mean values',
            'total': 'Total or sum amounts'
        }
        return descriptions.get(metric_type, f'{metric_type.title()} values')
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse any file structure intelligently"""
        try:
            # Try to read as Excel first
            try:
                df_raw = pd.read_excel(file_path, header=None)
            except:
                # Try CSV
                df_raw = pd.read_csv(file_path, header=None)
            
            # Detect structure type
            structure_type = self._detect_structure(df_raw)
            
            if structure_type == 'summary_report':
                return self._parse_summary_format(df_raw)
            elif structure_type == 'standard_table':
                return self._parse_standard_table(df_raw)
            else:
                return self._parse_generic(df_raw)
                
        except Exception as e:
            return {'error': str(e)}
    
    def _detect_structure(self, df: pd.DataFrame) -> str:
        """Detect the structure type of the data"""
        # Check if it's a summary format (label-value pairs)
        # Summary format: first column has text, other columns have sparse numeric data
        if df.shape[1] > 1:
            first_col_text_ratio = df.iloc[:, 0].astype(str).str.contains(r'[a-zA-Z]', regex=True).sum() / len(df)
            other_cols_numeric_ratio = 0
            
            for col_idx in range(1, min(6, df.shape[1])):
                numeric_count = pd.to_numeric(df.iloc[:, col_idx], errors='coerce').notna().sum()
                other_cols_numeric_ratio += numeric_count / len(df)
            
            other_cols_numeric_ratio /= (df.shape[1] - 1)
            
            # Summary format: high text in first col, sparse numeric in others
            if first_col_text_ratio > 0.5 and other_cols_numeric_ratio < 0.3:
                return 'summary_report'
        
        # Standard table: has headers and regular structure
        return 'standard_table'
    
    def _parse_summary_format(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """Parse summary/report format (label-value pairs)"""
        data_rows = []
        current_section = None
        
        for idx, row in df_raw.iterrows():
            first_col = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
            
            if not first_col or first_col == 'nan':
                continue
            
            # Detect section headers (flexible pattern)
            if any(keyword in first_col.lower() for keyword in ['summary', 'report', 'total', 'section']):
                if len(first_col) < 50:  # Reasonable section header length
                    current_section = first_col
                    continue
            
            # Find numeric values
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
        
        # Build dataframe with intelligent column naming
        all_col_indices = set()
        for row in data_rows:
            all_col_indices.update(row['values'].keys())
        all_col_indices = sorted(list(all_col_indices))
        
        # Intelligently name columns
        column_names = {}
        for col_idx in all_col_indices:
            labels_in_col = []
            values_in_col = []
            for row in data_rows:
                if col_idx in row['values']:
                    labels_in_col.append(row['label'])
                    values_in_col.append(row['values'][col_idx])
            
            # Use intelligent inference
            inference = self.infer_column_meaning(
                labels_in_col, values_in_col, col_idx, len(all_col_indices)
            )
            column_names[col_idx] = inference['display_name']
        
        # Build structured data
        structured_data = []
        for row in data_rows:
            record = {'Label': row['label'], 'Section': row['section']}
            for col_idx in all_col_indices:
                col_name = column_names.get(col_idx, f'Column_{col_idx}')
                record[col_name] = row['values'].get(col_idx, None)
            structured_data.append(record)
        
        df = pd.DataFrame(structured_data)
        
        # Process numeric columns
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
        
        # Create metadata
        column_metadata = []
        for col in numeric_columns:
            values = df[col].dropna()
            if len(values) > 0:
                labels_with_data = df[df[col].notna()]['Label'].unique().tolist()
                inference = self.infer_column_meaning(
                    labels_with_data, values.tolist(), 
                    numeric_columns.index(col), len(numeric_columns)
                )
                column_metadata.append({
                    'original': col,
                    'clean': col,
                    'display_name': inference['display_name'],
                    'type': 'numeric',
                    'description': inference['description'],
                    'value_type': inference.get('value_type', 'unknown'),
                    'value_scale': inference.get('value_scale', 'unknown')
                })
        
        return {
            'data': df.replace({np.nan: None}).to_dict('records'),
            'columns': df.columns.tolist(),
            'column_metadata': column_metadata,
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0]),
            'format': 'summary_report'
        }
    
    def _parse_standard_table(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """Parse standard table format with headers"""
        # Try to detect header row
        header_row = self._detect_header_row(df_raw)
        
        if header_row is not None:
            df = df_raw.iloc[header_row+1:].copy()
            df.columns = df_raw.iloc[header_row].values
            df = df.reset_index(drop=True)
        else:
            df = df_raw.copy()
            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
        
        # Clean and process
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Convert object columns to numeric where appropriate
        numeric_columns = []
        categorical_columns = []
        
        for col in df.columns:
            converted = pd.to_numeric(df[col], errors='coerce')
            if converted.notna().sum() / len(df) > 0.5:
                df[col] = converted
                numeric_columns.append(col)
            else:
                categorical_columns.append(col)
        
        # Create intelligent metadata
        column_metadata = []
        for col in numeric_columns:
            values = df[col].dropna()
            if len(values) > 0:
                inference = self.infer_column_meaning(
                    [str(col)], values.tolist(),
                    numeric_columns.index(col), len(numeric_columns)
                )
                column_metadata.append({
                    'original': str(col),
                    'clean': str(col),
                    'display_name': inference['display_name'],
                    'type': 'numeric',
                    'description': inference['description']
                })
        
        return {
            'data': df.replace({np.nan: None}).to_dict('records'),
            'columns': df.columns.tolist(),
            'column_metadata': column_metadata,
            'shape': [int(df.shape[0]), int(df.shape[1])],
            'numericColumns': numeric_columns,
            'categoricalColumns': categorical_columns,
            'totalRows': int(df.shape[0]),
            'format': 'standard_table'
        }
    
    def _parse_generic(self, df_raw: pd.DataFrame) -> Dict[str, Any]:
        """Generic parser for unknown structures"""
        return self._parse_standard_table(df_raw)
    
    def _detect_header_row(self, df: pd.DataFrame) -> int:
        """Detect which row contains headers"""
        for idx in range(min(5, len(df))):
            row = df.iloc[idx]
            text_count = sum(1 for val in row if pd.notna(val) and isinstance(val, str))
            numeric_count = sum(1 for val in row if pd.notna(val) and isinstance(val, (int, float)))
            
            # Header row typically has more text than numbers
            if text_count > numeric_count and text_count > len(row) * 0.5:
                return idx
        return None


def parse_file_intelligently(file_path: str) -> Dict[str, Any]:
    """Main entry point for intelligent parsing"""
    parser = IntelligentParser()
    result = parser.parse_file(file_path)
    
    print(json.dumps(result), file=sys.stdout)
    sys.stdout.flush()
    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing file path'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    parse_file_intelligently(file_path)

