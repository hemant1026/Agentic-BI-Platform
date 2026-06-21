import os
import sys
import json
import tempfile
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from process_data import process_file


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "sample.csv"
    path.write_text(
        "date,sales,region,product_category,quantity,price\n"
        "2024-01-01,15000,North,Electronics,50,300\n"
        "2024-01-02,12000,South,Clothing,80,150\n"
        "2024-01-03,18000,East,Electronics,60,300\n"
        "2024-01-04,9000,West,Food,100,90\n"
        "2024-01-05,22000,North,Electronics,70,314\n"
    )
    return str(path)


@pytest.fixture
def empty_csv(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("col_a,col_b\n")
    return str(path)


@pytest.fixture
def numeric_only_csv(tmp_path):
    path = tmp_path / "numeric.csv"
    path.write_text(
        "a,b,c\n"
        "1,2,3\n"
        "4,5,6\n"
        "7,8,9\n"
    )
    return str(path)


class TestProcessData:
    def test_loads_csv(self, sample_csv, capsys):
        process_file(sample_csv, "test_dataset")
        captured = capsys.readouterr()
        result = json.loads(captured.out.strip().split('\n')[-1])
        assert 'data' in result
        assert 'columns' in result
        assert len(result['data']) == 5

    def test_detects_numeric_columns(self, sample_csv, capsys):
        process_file(sample_csv, "test_dataset")
        captured = capsys.readouterr()
        result = json.loads(captured.out.strip().split('\n')[-1])
        assert 'sales' in result['numericColumns']
        assert 'quantity' in result['numericColumns']
        assert 'price' in result['numericColumns']

    def test_detects_categorical_columns(self, sample_csv, capsys):
        process_file(sample_csv, "test_dataset")
        captured = capsys.readouterr()
        result = json.loads(captured.out.strip().split('\n')[-1])
        assert 'region' in result['categoricalColumns']
        assert 'product_category' in result['categoricalColumns']

    def test_shape_correct(self, sample_csv, capsys):
        process_file(sample_csv, "test_dataset")
        captured = capsys.readouterr()
        result = json.loads(captured.out.strip().split('\n')[-1])
        assert result['shape'][0] == 5
        assert result['shape'][1] == 6

    def test_all_numeric_file(self, numeric_only_csv, capsys):
        process_file(numeric_only_csv, "test")
        captured = capsys.readouterr()
        result = json.loads(captured.out.strip().split('\n')[-1])
        assert len(result['numericColumns']) == 3
        assert len(result['categoricalColumns']) == 0

    def test_nonexistent_file(self):
        with pytest.raises(SystemExit):
            process_file("/nonexistent/path.csv", "test")


class TestDataStructureAgent:
    def test_analyze_returns_column_meanings(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({
            'sales': [100, 200, 300],
            'region': ['North', 'South', 'East'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        result = agent.analyze(df)
        assert 'column_meanings' in result
        assert 'sales' in result['column_meanings']
        assert 'region' in result['column_meanings']

    def test_numeric_stats_computed(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({'price': [10.0, 20.0, 30.0, 40.0, 50.0]})
        result = agent.analyze(df)
        stats = result['column_meanings']['price']['stats']
        assert stats['min'] == 10.0
        assert stats['max'] == 50.0
        assert stats['mean'] == 30.0

    def test_infer_meaning_financial(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({'revenue': [1000, 2000, 3000]})
        meaning = agent._infer_meaning(df, 'revenue')
        assert meaning == 'financial_metric'

    def test_infer_meaning_temporal(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({'date': ['2024-01-01', '2024-01-02']})
        meaning = agent._infer_meaning(df, 'date')
        assert meaning == 'temporal'

    def test_infer_meaning_location(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({'region': ['North', 'South', 'East']})
        meaning = agent._infer_meaning(df, 'region')
        assert meaning == 'location'

    def test_null_handling(self):
        from bi_agent_team import DataStructureAgent
        agent = DataStructureAgent()
        df = pd.DataFrame({'val': [1.0, np.nan, 3.0, np.nan, 5.0]})
        result = agent.analyze(df)
        assert result['column_meanings']['val']['null_count'] == 2
        assert result['column_meanings']['val']['null_percentage'] == 40.0


class TestVisualizationAgent:
    def test_recommends_scatter_for_two_numeric(self):
        from bi_agent_team import VisualizationAgent
        agent = VisualizationAgent()
        df = pd.DataFrame({'sales': [100, 200], 'quantity': [10, 20]})
        analysis = {'column_meanings': {}}
        recs = agent.recommend(df, analysis)
        types = [r['type'] for r in recs]
        assert 'scatter' in types

    def test_recommends_heatmap_for_many_numeric(self):
        from bi_agent_team import VisualizationAgent
        agent = VisualizationAgent()
        df = pd.DataFrame({
            'a': [1, 2, 3], 'b': [4, 5, 6],
            'c': [7, 8, 9], 'd': [10, 11, 12]
        })
        analysis = {'column_meanings': {}}
        recs = agent.recommend(df, analysis)
        types = [r['type'] for r in recs]
        assert 'heatmap' in types

    def test_recommends_bar_for_label_column(self):
        from bi_agent_team import VisualizationAgent
        agent = VisualizationAgent()
        df = pd.DataFrame({
            'Label': ['A', 'B', 'C'],
            'value': [100, 200, 300]
        })
        analysis = {'column_meanings': {}}
        recs = agent.recommend(df, analysis)
        types = [r['type'] for r in recs]
        assert 'bar' in types


class TestKPIAgent:
    def test_generates_kpis_for_numeric(self):
        from bi_agent_team import KPIAgent
        agent = KPIAgent()
        df = pd.DataFrame({'sales': [100, 200, 300, 400, 500]})
        analysis = {'column_meanings': {'sales': {'inferred_meaning': 'financial_metric'}}}
        kpis = agent.generate(df, analysis)
        assert 'sales' in kpis
        assert kpis['sales']['mean'] == 300.0
        assert kpis['sales']['sum'] == 1500.0
        assert kpis['sales']['count'] == 5

    def test_financial_metric_has_total(self):
        from bi_agent_team import KPIAgent
        agent = KPIAgent()
        df = pd.DataFrame({'revenue': [1000, 2000, 3000]})
        analysis = {'column_meanings': {'revenue': {'inferred_meaning': 'financial_metric'}}}
        kpis = agent.generate(df, analysis)
        assert 'total' in kpis['revenue']
        assert kpis['revenue']['total'] == 6000.0

    def test_handles_nulls_in_kpi(self):
        from bi_agent_team import KPIAgent
        agent = KPIAgent()
        df = pd.DataFrame({'val': [10.0, np.nan, 30.0, np.nan, 50.0]})
        analysis = {'column_meanings': {'val': {'inferred_meaning': 'numeric'}}}
        kpis = agent.generate(df, analysis)
        assert kpis['val']['count'] == 3
        assert kpis['val']['null_count'] == 2

    def test_kpi_display_name(self):
        from bi_agent_team import KPIAgent
        agent = KPIAgent()
        assert agent._get_kpi_name('total_sales', 'financial_metric') == 'Total Sales'
        assert agent._get_kpi_name('item_count', 'count_metric') == 'Item Count (Count)'
