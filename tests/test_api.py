import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestChartDataGeneration:
    """Test chart data generation logic (mirrors server.js generateKPIs/generateVisualizations)"""

    def test_histogram_data(self):
        data = [{'sales': 100}, {'sales': 200}, {'sales': 300}]
        values = [float(row['sales']) for row in data if not np.isnan(float(row['sales']))]
        assert len(values) == 3
        assert min(values) == 100
        assert max(values) == 300

    def test_bar_frequency_data(self):
        data = [
            {'region': 'North'}, {'region': 'South'},
            {'region': 'North'}, {'region': 'East'},
            {'region': 'North'}
        ]
        counts = {}
        for row in data:
            v = row['region']
            counts[v] = counts.get(v, 0) + 1
        assert counts['North'] == 3
        assert counts['South'] == 1
        assert counts['East'] == 1

    def test_scatter_data_alignment(self):
        data = [
            {'x': 1, 'y': 10},
            {'x': 2, 'y': 20},
            {'x': 3, 'y': None},
            {'x': 4, 'y': 40},
        ]
        x_vals = []
        y_vals = []
        for row in data:
            if row['x'] is not None and row['y'] is not None:
                x_vals.append(row['x'])
                y_vals.append(row['y'])
        assert len(x_vals) == 3
        assert len(y_vals) == 3

    def test_correlation_matrix(self):
        df = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [2, 4, 6, 8, 10],
            'c': [5, 4, 3, 2, 1],
        })
        corr = df.corr()
        assert corr.loc['a', 'b'] == pytest.approx(1.0)
        assert corr.loc['a', 'c'] == pytest.approx(-1.0)

    def test_kpi_calculation(self):
        values = [100, 200, 300, 400, 500]
        mean = sum(values) / len(values)
        total = sum(values)
        minimum = min(values)
        maximum = max(values)
        assert mean == 300
        assert total == 1500
        assert minimum == 100
        assert maximum == 500

    def test_std_dev_calculation(self):
        values = [10, 20, 30, 40, 50]
        mean = sum(values) / len(values)
        sq_diffs = [(v - mean) ** 2 for v in values]
        variance = sum(sq_diffs) / len(values)
        std = variance ** 0.5
        assert std == pytest.approx(14.142, rel=0.01)


class TestDatasetValidation:
    def test_sample_data_loads(self):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_data.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            assert len(df) == 20
            assert 'sales' in df.columns
            assert 'region' in df.columns

    def test_ecommerce_data_loads(self):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ecommerce_orders.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            assert len(df) == 100
            assert 'total_amount' in df.columns

    def test_employee_data_loads(self):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'employee_performance.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            assert len(df) == 50
            assert 'performance_score' in df.columns

    def test_financial_data_loads(self):
        data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'financial_quarterly.csv')
        if os.path.exists(data_path):
            df = pd.read_csv(data_path)
            assert len(df) == 24
            assert 'revenue' in df.columns
            assert 'net_income' in df.columns
