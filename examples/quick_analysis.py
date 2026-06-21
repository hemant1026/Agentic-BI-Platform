#!/usr/bin/env python3
"""
Quick analysis example - demonstrates using the BI agent team programmatically.

Usage:
    python examples/quick_analysis.py data/sample_data.csv
"""
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from bi_agent_team import DataStructureAgent, VisualizationAgent, KPIAgent
import pandas as pd


def analyze_file(file_path: str):
    df = pd.read_csv(file_path)
    print(f"Loaded {file_path}: {df.shape[0]} rows, {df.shape[1]} columns\n")

    structure_agent = DataStructureAgent()
    viz_agent = VisualizationAgent()
    kpi_agent = KPIAgent()

    analysis = structure_agent.analyze(df)

    print("=" * 60)
    print("COLUMN ANALYSIS")
    print("=" * 60)
    for col, info in analysis['column_meanings'].items():
        meaning = info['inferred_meaning']
        nulls = info['null_percentage']
        print(f"  {col:25s}  type={meaning:20s}  nulls={nulls:.1f}%")
        if 'stats' in info:
            s = info['stats']
            print(f"  {'':25s}  min={s['min']:.2f}  max={s['max']:.2f}  mean={s['mean']:.2f}")

    kpis = kpi_agent.generate(df, analysis)
    print(f"\n{'=' * 60}")
    print("KPIs")
    print("=" * 60)
    for name, kpi in kpis.items():
        display = kpi.get('display_name', name)
        print(f"  {display:25s}  mean={kpi['mean']:.2f}  sum={kpi['sum']:.2f}  count={kpi['count']}")

    vizs = viz_agent.recommend(df, analysis)
    print(f"\n{'=' * 60}")
    print("RECOMMENDED VISUALIZATIONS")
    print("=" * 60)
    for v in vizs:
        print(f"  [{v['priority']:6s}] {v['type']:10s}  {v['title']}")

    print(f"\nAnalysis complete. {len(kpis)} KPIs, {len(vizs)} visualizations generated.")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python examples/quick_analysis.py <csv_file>")
        sys.exit(1)
    analyze_file(sys.argv[1])
