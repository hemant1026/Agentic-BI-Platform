import os
import sys
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


class TestIntelligentParser:
    def test_classify_value_scale(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        assert parser._classify_value_scale(2000000, 0, 500000) == 'large'
        assert parser._classify_value_scale(50000, 100, 25000) == 'medium'
        assert parser._classify_value_scale(500, 10, 200) == 'small'
        assert parser._classify_value_scale(50, 1, 25) == 'tiny'

    def test_classify_value_type(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        assert parser._classify_value_type(5000, 100, 2500, 10) == 'amount'

    def test_detect_header_row(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        df = pd.DataFrame([
            ['Name', 'Age', 'City'],
            ['Alice', 30, 'NYC'],
            ['Bob', 25, 'LA'],
        ])
        assert parser._detect_header_row(df) == 0

    def test_detect_structure_standard(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        df = pd.DataFrame({
            0: ['Name', 'Alice', 'Bob'],
            1: ['Sales', 100, 200],
            2: ['Region', 'N', 'S'],
        })
        assert parser._detect_structure(df) == 'standard_table'

    def test_infer_column_meaning_revenue(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        result = parser.infer_column_meaning(
            ['net sales', 'gross revenue'], [5000, 8000], 0, 3
        )
        assert 'display_name' in result
        assert result['display_name'] is not None

    def test_financial_name_with_modifier(self):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        assert 'Net' in parser._create_financial_name('revenue', 'net sales total', 'medium')
        assert 'Gross' in parser._create_financial_name('revenue', 'gross sales total', 'medium')


class TestSuperIntelligentParser:
    def test_compute_precise_stats(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        stats = parser._compute_precise_stats([10, 20, 30, 40, 50])
        assert stats['min'] == 10
        assert stats['max'] == 50
        assert stats['mean'] == 30
        assert stats['count'] == 5
        assert stats['is_integer'] is True
        assert stats['is_positive'] is True

    def test_compute_stats_empty(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        assert parser._compute_precise_stats([]) == {}

    def test_analyze_labels_precisely(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        result = parser._analyze_labels_precisely(
            ['net sales', 'tax', 'total'], 'net sales tax total'
        )
        assert result['confidence'] > 0.5
        assert len(result['primary_terms']) > 0

    def test_analyze_values_percentage(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        stats = {'is_percentage_range': True, 'max': 85, 'min': 10, 'mean': 45,
                 'is_integer': False}
        result = parser._analyze_values_precisely([10, 45, 85], stats)
        assert result['type'] == 'percentage'

    def test_analyze_values_count(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        stats = {'is_percentage_range': False, 'max': 500, 'min': 10, 'mean': 200,
                 'is_integer': True}
        result = parser._analyze_values_precisely([10, 200, 500], stats)
        assert result['type'] == 'count'

    def test_create_safe_name(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        result = parser._create_safe_name(3, 'amount')
        assert result['display_name'] == 'Data Column 3'
        assert result['confidence'] == 0.5

    def test_precise_description_sales(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        desc = parser._create_precise_description('Total Sales', {'min': 100, 'max': 5000})
        assert 'Sales' in desc or 'Revenue' in desc

    def test_precise_description_tax(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        desc = parser._create_precise_description('Tax Amount', {'sum': 1500})
        assert 'Tax' in desc

    def test_detect_structure(self):
        from super_intelligent_parser import SuperIntelligentParser
        parser = SuperIntelligentParser()
        df = pd.DataFrame({
            0: ['Name', 'Alice', 'Bob', 'Charlie'],
            1: [100, 200, 300, 400],
            2: [50, 60, 70, 80],
        })
        result = parser._detect_structure(df)
        assert result in ['summary_report', 'standard_table']


class TestEndToEndParsing:
    def test_parse_standard_csv(self, tmp_path):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        csv_path = tmp_path / "test.csv"
        csv_path.write_text(
            "product,revenue,units\n"
            "Widget A,5000,100\n"
            "Widget B,8000,150\n"
            "Widget C,3000,60\n"
        )
        result = parser.parse_file(str(csv_path))
        assert 'error' not in result
        assert len(result['data']) == 3
        assert len(result['numericColumns']) >= 1

    def test_parse_preserves_data(self, tmp_path):
        from intelligent_parser import IntelligentParser
        parser = IntelligentParser()
        csv_path = tmp_path / "test2.csv"
        csv_path.write_text(
            "name,value\n"
            "A,100\n"
            "B,200\n"
        )
        result = parser.parse_file(str(csv_path))
        assert result['totalRows'] == 2
        assert result['shape'][0] == 2
