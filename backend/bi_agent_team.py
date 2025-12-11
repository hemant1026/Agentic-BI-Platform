#!/usr/bin/env python3
"""
BI Agent Team - Multiple specialized agents for data analysis
"""
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class DataStructureAgent:
    """Agent specialized in understanding data structure"""
    
    def analyze(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data structure and infer column meanings"""
        analysis = {
            'column_meanings': {},
            'data_quality': {},
            'recommendations': []
        }
        
        for col in df.columns:
            col_analysis = {
                'dtype': str(df[col].dtype),
                'null_count': int(df[col].isnull().sum()),
                'null_percentage': float(df[col].isnull().sum() / len(df) * 100),
                'unique_count': int(df[col].nunique()),
                'inferred_meaning': self._infer_meaning(df, col)
            }
            
            if df[col].dtype in [np.int64, np.float64]:
                col_analysis['stats'] = {
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median())
                }
            
            analysis['column_meanings'][col] = col_analysis
        
        return analysis
    
    def _infer_meaning(self, df: pd.DataFrame, col: str) -> str:
        """Infer the meaning of a column from its data - dynamic pattern matching"""
        sample = df[col].dropna().head(20).astype(str).str.lower()
        sample_str = ' '.join(sample.tolist())
        col_name_lower = str(col).lower()
        combined_text = f'{col_name_lower} {sample_str}'
        
        # Dynamic pattern matching - no hardcoding
        patterns = {
            'financial_metric': ['sales', 'revenue', 'amount', 'total', 'price', 'cost', 'income', 'expense', 'profit', 'margin'],
            'temporal': ['date', 'time', 'day', 'month', 'year', 'timestamp', 'period', 'quarter'],
            'count_metric': ['count', 'number', 'quantity', 'items', 'units', 'qty'],
            'identifier': ['id', 'code', 'identifier', 'key', 'ref', 'reference'],
            'percentage': ['percent', 'percentage', 'rate', 'ratio', 'pct'],
            'location': ['location', 'place', 'region', 'city', 'state', 'country', 'address'],
            'category': ['category', 'type', 'class', 'group', 'segment', 'kind']
        }
        
        # Score each pattern
        scores = {}
        for meaning, keywords in patterns.items():
            score = sum(1 for keyword in keywords if keyword in combined_text)
            if score > 0:
                scores[meaning] = score
        
        # Return highest scoring pattern
        if scores:
            return max(scores, key=scores.get)
        
        # Fallback to data characteristics
        if df[col].nunique() < 20:
            return 'category'
        elif df[col].dtype in [np.int64, np.float64]:
            return 'numeric'
        else:
            return 'text_data'


def _clean_name(name: str) -> str:
    """Helper to clean column names"""
    return name.replace('_', ' ').replace('Column', 'Value').title()

class VisualizationAgent:
    """Agent specialized in recommending visualizations"""
    
    def recommend(self, df: pd.DataFrame, column_analysis: Dict, metadata: List[Dict] = None) -> List[Dict[str, Any]]:
        """Recommend appropriate visualizations"""
        recommendations = []
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
        
        # Create metadata map for better naming
        metadata_map = {}
        if metadata:
            for meta in metadata:
                metadata_map[meta.get('clean', meta.get('original', ''))] = meta
        
        # 1. For summary format, create bar charts showing values by label
        if 'Label' in categorical_cols and len(numeric_cols) > 0:
            # Top values chart
            for col in numeric_cols[:2]:
                display_name = self._get_display_name(col, column_analysis, metadata_map)
                recommendations.append({
                    'type': 'bar',
                    'title': f'{display_name} by Category',
                    'xColumn': 'Label',
                    'yColumn': col,
                    'datasetName': 'current',
                    'reason': 'Shows values by category/label',
                    'priority': 'high'
                })
        
        # 2. Distribution analysis for numeric columns (if not summary format)
        if 'Label' not in categorical_cols:
            for col in numeric_cols[:2]:
                if df[col].notna().sum() > 10:
                    display_name = self._get_display_name(col, column_analysis, metadata_map)
                    recommendations.append({
                        'type': 'histogram',
                        'title': f'Distribution of {display_name}',
                        'xColumn': col,
                        'yColumn': None,
                        'datasetName': 'current',
                        'reason': 'Shows data distribution and outliers',
                        'priority': 'high'
                    })
        
        # 3. Category frequency for categorical (non-label columns)
        for col in categorical_cols:
            if col != 'Label' and col != 'Section' and df[col].nunique() <= 15 and df[col].notna().sum() > 5:
                display_name = self._get_display_name(col, column_analysis, metadata_map)
                recommendations.append({
                    'type': 'bar',
                    'title': f'Frequency: {display_name}',
                    'xColumn': col,
                    'yColumn': None,
                    'datasetName': 'current',
                    'reason': 'Shows category distribution',
                    'priority': 'medium'
                })
        
        # 4. Relationships between numeric columns
        if len(numeric_cols) >= 2:
            display_x = self._get_display_name(numeric_cols[0], column_analysis, metadata_map)
            display_y = self._get_display_name(numeric_cols[1], column_analysis, metadata_map)
            recommendations.append({
                'type': 'scatter',
                'title': f'{display_x} vs {display_y}',
                'xColumn': numeric_cols[0],
                'yColumn': numeric_cols[1],
                'datasetName': 'current',
                'reason': 'Shows relationship between two metrics',
                'priority': 'high'
            })
        
        # 5. Correlation heatmap
        if len(numeric_cols) >= 3:
            recommendations.append({
                'type': 'heatmap',
                'title': 'Correlation Matrix',
                'xColumn': None,
                'yColumn': None,
                'columns': numeric_cols[:8],
                'datasetName': 'current',
                'reason': 'Shows correlations between all numeric metrics',
                'priority': 'medium'
            })
        
        return recommendations
    
    def _get_display_name(self, col: str, analysis: Dict, metadata_map: Dict = None) -> str:
        """Get a human-readable display name for a column"""
        # Check metadata first
        if metadata_map and col in metadata_map:
            meta = metadata_map[col]
            if 'display_name' in meta:
                return meta['display_name']
            if 'clean' in meta and meta['clean'] != col:
                return meta['clean'].replace('_', ' ').title()
        
        # Check analysis
        if col in analysis.get('column_meanings', {}):
            meaning = analysis['column_meanings'][col].get('inferred_meaning', '')
            if meaning == 'financial_metric':
                return col.replace('_', ' ').replace('Column', 'Value').title()
            elif meaning == 'count_metric':
                return col.replace('_', ' ').replace('Column', 'Count').title()
        
        # Clean up column name
        name = col.replace('_', ' ').replace('Unnamed:', 'Column').title()
        if name.startswith('Column'):
            return f'Value {name}'
        return name


class KPIAgent:
    """Agent specialized in KPI generation"""
    
    def generate(self, df: pd.DataFrame, column_analysis: Dict) -> Dict[str, Any]:
        """Generate meaningful KPIs"""
        kpis = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        for col in numeric_cols:
            values = df[col].dropna()
            if len(values) > 0:
                meaning = column_analysis.get('column_meanings', {}).get(col, {}).get('inferred_meaning', '')
                
                kpi_data = {
                    'mean': float(values.mean()),
                    'median': float(values.median()),
                    'min': float(values.min()),
                    'max': float(values.max()),
                    'std': float(values.std()),
                    'count': int(values.count()),
                    'sum': float(values.sum()),
                    'null_count': int(df[col].isnull().sum()),
                    'null_percentage': float(df[col].isnull().sum() / len(df) * 100),
                    'display_name': self._get_kpi_name(col, meaning)
                }
                
                # Add context-specific metrics
                if meaning == 'financial_metric':
                    kpi_data['total'] = float(values.sum())
                    kpi_data['average'] = float(values.mean())
                
                kpis[col] = kpi_data
        
        return kpis
    
    def _get_kpi_name(self, col: str, meaning: str) -> str:
        """Get a meaningful KPI name"""
        # Clean up column name
        name = col.replace('_', ' ').replace('Unnamed:', 'Column').title()
        
        if meaning == 'financial_metric':
            if 'sales' in col.lower() or 'revenue' in col.lower():
                return 'Total Sales'
            elif 'amount' in col.lower() or 'total' in col.lower():
                return 'Total Amount'
            else:
                return name
        elif meaning == 'count_metric':
            return name + ' (Count)'
        else:
            return name


def analyze_with_bi_team(file_path: str) -> Dict[str, Any]:
    """Use BI agent team to analyze data"""
    try:
        # First try smart parser for summary formats
        use_smart_parser = False
        structure_result = None
        
        try:
            import subprocess
            import os
            # Try super intelligent parser first (most accurate)
            script_path = os.path.join(os.path.dirname(__file__), 'super_intelligent_parser.py')
            result = subprocess.run(
                ['python3', script_path, file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                structure_result = json.loads(result.stdout)
                if 'error' not in structure_result:
                    use_smart_parser = True
        except:
            # Fallback to intelligent parser
            try:
                script_path = os.path.join(os.path.dirname(__file__), 'intelligent_parser.py')
                result = subprocess.run(
                    ['python3', script_path, file_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    structure_result = json.loads(result.stdout)
                    if 'error' not in structure_result:
                        use_smart_parser = True
            except:
                # Final fallback to v2 parser
                try:
                    script_path = os.path.join(os.path.dirname(__file__), 'smart_data_parser_v2.py')
                    result = subprocess.run(
                        ['python3', script_path, file_path],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode == 0:
                        structure_result = json.loads(result.stdout)
                        if 'error' not in structure_result:
                            use_smart_parser = True
                except:
                    pass
        
        # Fall back to basic process_data if smart parser fails
        if not use_smart_parser:
            try:
                import subprocess
                import os
                script_path = os.path.join(os.path.dirname(__file__), 'process_data.py')
                result = subprocess.run(
                    ['python3', script_path, file_path, 'dataset'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0:
                    structure_result = json.loads(result.stdout)
            except Exception as e:
                error_result = {'error': f'Failed to analyze data: {str(e)}'}
                print(json.dumps(error_result), file=sys.stdout)
                sys.stdout.flush()
                sys.exit(1)
        
        if not structure_result or 'error' in structure_result:
            print(json.dumps(structure_result if structure_result else {'error': 'No result'}), file=sys.stdout)
            sys.stdout.flush()
            sys.exit(1)
        
        # Reconstruct dataframe
        df = pd.DataFrame(structure_result['data'])
        df.columns = structure_result['columns']
        
        # Convert nulls back to NaN for pandas
        df = df.replace({None: np.nan})
        
        # Convert numeric columns
        for col in structure_result['numericColumns']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Run BI agent team
        structure_agent = DataStructureAgent()
        viz_agent = VisualizationAgent()
        kpi_agent = KPIAgent()
        
        column_analysis = structure_agent.analyze(df)
        metadata = structure_result.get('column_metadata', [])
        visualizations = viz_agent.recommend(df, column_analysis, metadata)
        kpis = kpi_agent.generate(df, column_analysis)
        
        # Enhance visualization titles with metadata
        for viz in visualizations:
            if metadata:
                for meta in metadata:
                    if viz.get('xColumn') == meta.get('clean') or viz.get('xColumn') == meta.get('original'):
                        if 'display_name' in meta:
                            x_name = meta['display_name']
                            if viz.get('yColumn'):
                                # Find y metadata
                                for y_meta in metadata:
                                    if viz.get('yColumn') == y_meta.get('clean') or viz.get('yColumn') == y_meta.get('original'):
                                        if 'display_name' in y_meta:
                                            viz['title'] = f'{x_name} vs {y_meta["display_name"]}'
                                        else:
                                            viz['title'] = f'{x_name} vs {_clean_name(viz.get("yColumn"))}'
                                        break
                            else:
                                # Update title with better name
                                if 'Distribution' in viz['title']:
                                    viz['title'] = f'Distribution of {x_name}'
                                elif 'Frequency' in viz['title']:
                                    viz['title'] = f'{x_name} by Category'
                                else:
                                    viz['title'] = viz['title'].replace(str(viz.get('xColumn', '')), x_name)
                        break
        
        result = {
            'data': structure_result['data'],
            'columns': structure_result['columns'],
            'column_metadata': structure_result.get('column_metadata', []),
            'shape': structure_result['shape'],
            'numericColumns': structure_result['numericColumns'],
            'categoricalColumns': structure_result['categoricalColumns'],
            'kpis': kpis,
            'visualizations': visualizations,
            'column_analysis': column_analysis,
            'insights': structure_result.get('insights', []),
            'totalRows': structure_result['totalRows']
        }
        
        # Output only JSON to stdout (errors go to stderr)
        print(json.dumps(result), file=sys.stdout)
        sys.stdout.flush()
        return result
        
    except Exception as e:
        import traceback
        error_result = {'error': str(e), 'traceback': traceback.format_exc()}
        print(json.dumps(error_result), file=sys.stdout)
        sys.stdout.flush()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Missing file path'}))
        sys.exit(1)
    
    file_path = sys.argv[1]
    analyze_with_bi_team(file_path)

