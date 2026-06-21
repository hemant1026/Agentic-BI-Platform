#!/usr/bin/env python3
"""
Batch analysis example - analyze all datasets in a directory and output a summary report.

Usage:
    python examples/batch_analysis.py data/
"""
import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from bi_agent_team import DataStructureAgent, VisualizationAgent, KPIAgent
import pandas as pd


def analyze_directory(directory: str):
    csv_files = glob.glob(os.path.join(directory, '*.csv'))
    if not csv_files:
        print(f"No CSV files found in {directory}")
        return

    print(f"Found {len(csv_files)} datasets in {directory}\n")
    print("=" * 80)

    summary = []

    for file_path in sorted(csv_files):
        filename = os.path.basename(file_path)
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            print(f"  SKIP {filename}: {e}")
            continue

        structure_agent = DataStructureAgent()
        kpi_agent = KPIAgent()
        viz_agent = VisualizationAgent()

        analysis = structure_agent.analyze(df)
        kpis = kpi_agent.generate(df, analysis)
        vizs = viz_agent.recommend(df, analysis)

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        categorical_cols = df.select_dtypes(exclude='number').columns.tolist()

        print(f"\n  {filename}")
        print(f"  {'─' * 60}")
        print(f"  Rows: {len(df)}  Columns: {len(df.columns)}  "
              f"Numeric: {len(numeric_cols)}  Categorical: {len(categorical_cols)}")
        print(f"  KPIs: {len(kpis)}  Visualizations: {len(vizs)}")

        if kpis:
            top_kpi = max(kpis.items(), key=lambda x: x[1].get('sum', 0))
            print(f"  Top metric: {top_kpi[0]} (sum={top_kpi[1]['sum']:.2f})")

        summary.append({
            'file': filename,
            'rows': len(df),
            'columns': len(df.columns),
            'kpis': len(kpis),
            'visualizations': len(vizs),
        })

    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print("=" * 80)
    total_rows = sum(s['rows'] for s in summary)
    total_kpis = sum(s['kpis'] for s in summary)
    total_vizs = sum(s['visualizations'] for s in summary)
    print(f"  Datasets analyzed: {len(summary)}")
    print(f"  Total rows processed: {total_rows}")
    print(f"  Total KPIs generated: {total_kpis}")
    print(f"  Total visualizations recommended: {total_vizs}")


if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else 'data/'
    analyze_directory(directory)
