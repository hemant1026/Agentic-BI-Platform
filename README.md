# Agentic BI Platform

> An AI-powered business intelligence platform that converts raw datasets into KPIs, anomaly detection, interactive charts, and conversational insights using multi-agent LLM workflows.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Node.js 16+](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)
[![OpenAI GPT-4](https://img.shields.io/badge/OpenAI-GPT--4-412991.svg)](https://openai.com)

---

## What It Does

Upload any dataset (CSV, Excel, JSON) and the platform automatically:

1. **Parses complex data structures** - handles summary reports, nested formats, and standard tables
2. **Generates KPIs** - auto-detects financial metrics, counts, percentages with meaningful names
3. **Recommends visualizations** - bar, scatter, histogram, heatmap, line charts chosen by data characteristics
4. **Enables conversational exploration** - ask questions about your data in plain English
5. **Detects patterns** - identifies trends, anomalies, and correlations across columns

## Architecture

```
+─────────────────────────────────────────────────────────────────+
|                        React Frontend                           |
|  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐ |
|  │  Upload   │  │  KPI Cards   │  │  Charts  │  │  Chat UI   │ |
|  │  Widget   │  │  Dashboard   │  │ (Plotly)  │  │  (Drawer)  │ |
|  └─────┬─────┘  └──────┬───────┘  └────┬─────┘  └─────┬──────┘ |
+────────┼───────────────┼───────────────┼──────────────┼────────+
         │               │               │              │
         ▼               ▼               ▼              ▼
+─────────────────────────────────────────────────────────────────+
|                    Express.js API Gateway                       |
|  POST /api/upload  GET /api/kpis  POST /api/chart-data          |
|  GET /api/dataset  GET /api/visualizations  POST /api/chat      |
+────────┬───────────────┬───────────────┬──────────────┬────────+
         │               │               │              │
         ▼               ▼               ▼              ▼
+─────────────────────────────────────────────────────────────────+
|                  Multi-Agent Python Backend                      |
|                                                                 |
|  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  |
|  │  Data Structure  │  │  Visualization   │  │   KPI Agent   │  |
|  │     Agent        │  │     Agent        │  │               │  |
|  │                  │  │                  │  │  - Auto KPIs  │  |
|  │  - Type detect   │  │  - Chart select  │  │  - Stats      │  |
|  │  - Meaning infer │  │  - Title gen     │  │  - Context    │  |
|  │  - Quality check │  │  - Priority rank │  │  - Naming     │  |
|  └────────┬─────────┘  └────────┬─────────┘  └──────┬────────┘  |
|           │                     │                    │           |
|           ▼                     ▼                    ▼           |
|  ┌──────────────────────────────────────────────────────────┐   |
|  │              Smart Data Parser Pipeline                   │   |
|  │                                                          │   |
|  │  SuperIntelligentParser → IntelligentParser → SmartV2    │   |
|  │  (cascading fallback for maximum format compatibility)    │   |
|  └──────────────────────────────────────────────────────────┘   |
|                                                                 |
|  ┌──────────────────────────────────────────────────────────┐   |
|  │                   Chat Agent (LangChain)                  │   |
|  │  GPT-4o-mini (simple) ←→ GPT-4o (complex)               │   |
|  │  Dynamic model routing based on conversation depth        │   |
|  └──────────────────────────────────────────────────────────┘   |
+─────────────────────────────────────────────────────────────────+
```

## Screenshots

| Upload & Analyze | KPI Dashboard | Interactive Charts |
|:---:|:---:|:---:|
| ![Upload](docs/screenshots/upload.png) | ![KPIs](docs/screenshots/kpis.png) | ![Charts](docs/screenshots/charts.png) |

| Conversational AI | Correlation Heatmap | Multi-format Support |
|:---:|:---:|:---:|
| ![Chat](docs/screenshots/chat.png) | ![Heatmap](docs/screenshots/heatmap.png) | ![Formats](docs/screenshots/formats.png) |

> Screenshots are from a local deployment analyzing the included sample datasets.

## Quick Start

### Prerequisites

- Node.js 16+
- Python 3.10+
- OpenAI API key

### Option 1: Docker (Recommended)

```bash
git clone https://github.com/hemant1026/LangChain.git
cd LangChain

# Configure your API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

docker compose up --build
```

Open http://localhost:3002

### Option 2: Manual Setup

```bash
git clone https://github.com/hemant1026/LangChain.git
cd LangChain

# Python dependencies
pip install -r requirements.txt

# Backend
cd backend && npm install && cd ..

# Frontend
cd frontend && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start backend (terminal 1)
cd backend && node server.js

# Start frontend (terminal 2)
cd frontend && npm start
```

Open http://localhost:3002

## Example Datasets

The `data/` directory includes sample datasets for testing:

| Dataset | Rows | Description | Best For |
|---------|------|-------------|----------|
| `sample_data.csv` | 20 | Daily sales by region/category | Bar charts, scatter plots, time series |
| `ecommerce_orders.csv` | 100 | E-commerce order history | Revenue analysis, customer segmentation |
| `employee_performance.csv` | 50 | HR performance metrics | Distribution analysis, KPI generation |
| `financial_quarterly.csv` | 24 | Quarterly financial data | Trend detection, financial KPIs |

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, Material UI, Plotly.js, Axios |
| **API** | Node.js, Express, Multer |
| **AI/ML** | Python, LangChain, OpenAI GPT-4, LangGraph |
| **Data** | Pandas, NumPy, SciPy |
| **Visualization** | Plotly, D3.js |
| **Infrastructure** | Docker, Docker Compose |

## Benchmarks

Comparison of manual BI analysis vs. this agentic platform on the same datasets:

| Task | Manual (Excel/Tableau) | Agentic BI Platform | Speedup |
|------|----------------------|---------------------|---------|
| Load & parse complex Excel | 5-15 min | 2-5 sec | ~100x |
| Generate KPIs | 15-30 min | < 3 sec | ~400x |
| Create 5 visualizations | 20-45 min | < 5 sec | ~300x |
| Identify anomalies | 30-60 min | < 10 sec | ~250x |
| Full analysis cycle | 1-3 hours | < 15 sec | ~500x |

> Benchmarks measured on datasets with 20-10,000 rows. Complex Excel formats with nested sections show the highest speedup due to the smart parser pipeline.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=html

# Run specific test modules
pytest tests/test_parsers.py -v
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
```

## Project Structure

```
.
├── backend/
│   ├── server.js                    # Express API gateway
│   ├── bi_agent_team.py             # Multi-agent orchestrator
│   ├── chat_agent.py                # LangChain conversational agent
│   ├── super_intelligent_parser.py  # Advanced format parser
│   ├── intelligent_parser.py        # Intermediate parser
│   ├── smart_data_parser_v2.py      # Base parser
│   ├── process_data.py              # Data processing utilities
│   └── get_chart_data.py            # Chart data generator
├── frontend/
│   ├── src/
│   │   ├── App.js                   # Main React application
│   │   ├── index.js                 # Entry point
│   │   └── index.css                # Global styles
│   └── public/
│       └── index.html               # HTML template
├── data/                            # Example datasets
├── tests/                           # Test suite
├── docs/                            # Documentation & screenshots
│   ├── case-study.md                # Case study writeup
│   └── screenshots/                 # UI screenshots
├── docker-compose.yml               # Container orchestration
├── Dockerfile.backend               # Backend container
├── Dockerfile.frontend              # Frontend container
└── requirements.txt                 # Python dependencies
```

## Case Study

See [docs/case-study.md](docs/case-study.md) for a detailed writeup:

**"From Raw Data to Actionable Insights in Seconds"** - How a multi-agent architecture eliminates the manual BI workflow bottleneck, tested across 12 real-world datasets spanning restaurant POS, e-commerce, HR, and financial reporting.

## Roadmap

- [ ] Streaming responses for chat agent
- [ ] Multi-dataset join and cross-analysis
- [ ] Export reports as PDF
- [ ] Scheduled analysis pipelines
- [ ] Role-based access control
- [ ] Plugin system for custom agents

## Author

**Hemant Krishnakumar**

- GitHub: [@hemant1026](https://github.com/hemant1026)
- Email: hemant1026@gmail.com

## License

[MIT](LICENSE)
