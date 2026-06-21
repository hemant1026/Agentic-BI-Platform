# Architecture

## System Overview

The Agentic BI Platform is a three-tier application with a multi-agent AI backend that converts raw datasets into structured business intelligence outputs.

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CLIENT TIER                                   │
│                                                                        │
│  React 18 SPA                                                          │
│  ┌─────────────┐  ┌───────────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ FileUpload   │  │ KPIDashboard  │  │ ChartView│  │ ChatDrawer   │  │
│  │              │  │               │  │ (Plotly)  │  │              │  │
│  │ - drag/drop  │  │ - auto KPIs   │  │ - bar    │  │ - NL queries │  │
│  │ - CSV/XLS/   │  │ - stats cards │  │ - scatter│  │ - context    │  │
│  │   JSON       │  │ - progress    │  │ - heatmap│  │ - history    │  │
│  └──────┬───────┘  └───────┬───────┘  │ - line   │  └──────┬───────┘  │
│         │                  │          │ - hist   │         │          │
│         │                  │          └────┬─────┘         │          │
└─────────┼──────────────────┼───────────────┼───────────────┼──────────┘
          │                  │               │               │
          ▼                  ▼               ▼               ▼
┌────────────────────────────────────────────────────────────────────────┐
│                          API TIER                                      │
│                                                                        │
│  Express.js (Node 18)                                                  │
│                                                                        │
│  Endpoints:                                                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ POST /api/upload     - File ingestion + full analysis pipeline  │   │
│  │ GET  /api/dataset/:n - Retrieve stored dataset                 │   │
│  │ GET  /api/kpis/:n    - Retrieve generated KPIs                 │   │
│  │ GET  /api/viz/:n     - Retrieve visualization specs            │   │
│  │ POST /api/chart-data - Generate chart data from stored dataset  │   │
│  │ POST /api/chat       - Conversational analysis via LangChain    │   │
│  │ GET  /api/datasets   - List all loaded datasets                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│  In-memory stores: datasets Map, visualizations Map, kpis Map          │
│  File handling: Multer (50MB limit), temp storage in uploads/          │
│                                                                        │
│  IPC: child_process.spawn → Python scripts (JSON over stdout)          │
└────────┬───────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       AGENT TIER (Python)                              │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    PARSER PIPELINE                                │  │
│  │                                                                   │  │
│  │  Input: raw file path                                            │  │
│  │                                                                   │  │
│  │  Stage 1: SuperIntelligentParser                                  │  │
│  │    - Ultra-precise column naming via multi-signal analysis        │  │
│  │    - Label combination analysis (e.g., "Net Sales" + "Tax" +     │  │
│  │      "Gratuity" → "Total Revenue")                               │  │
│  │    - Statistical validation of inferred names                     │  │
│  │    - Handles summary/report formats with nested sections          │  │
│  │    ↓ (fallback on failure)                                        │  │
│  │                                                                   │  │
│  │  Stage 2: IntelligentParser                                       │  │
│  │    - Semantic pattern matching for financial/operational terms     │  │
│  │    - Value scale classification (large/medium/small/tiny)         │  │
│  │    - Context-aware naming with modifiers                          │  │
│  │    ↓ (fallback on failure)                                        │  │
│  │                                                                   │  │
│  │  Stage 3: SmartDataParserV2                                       │  │
│  │    - Section-based parsing for summary formats                    │  │
│  │    - Position-aware column naming                                 │  │
│  │    ↓ (fallback on failure)                                        │  │
│  │                                                                   │  │
│  │  Stage 4: ProcessData (base)                                      │  │
│  │    - Multi-strategy file loading (CSV, Excel, JSON, TSV)          │  │
│  │    - Auto-detection of header rows                                │  │
│  │    - Type coercion with threshold-based numeric detection         │  │
│  │                                                                   │  │
│  │  Output: {data, columns, column_metadata, numericColumns,         │  │
│  │           categoricalColumns, shape, totalRows}                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    ANALYSIS AGENTS                                │  │
│  │                                                                   │  │
│  │  DataStructureAgent                                               │  │
│  │    Input: DataFrame                                               │  │
│  │    Process: For each column →                                     │  │
│  │      - dtype detection                                            │  │
│  │      - null analysis (count, percentage)                          │  │
│  │      - uniqueness analysis                                        │  │
│  │      - semantic inference (financial, temporal, category, etc.)   │  │
│  │      - statistical summary (min, max, mean, median)               │  │
│  │    Output: {column_meanings, data_quality, recommendations}       │  │
│  │                                                                   │  │
│  │  VisualizationAgent                                               │  │
│  │    Input: DataFrame + column_analysis + column_metadata           │  │
│  │    Process:                                                       │  │
│  │      - Label+numeric → bar charts (by category)                  │  │
│  │      - Continuous numeric → histograms (distribution)            │  │
│  │      - Low-cardinality categorical → frequency bar charts        │  │
│  │      - Two numeric → scatter plots (relationships)               │  │
│  │      - 3+ numeric → correlation heatmap                          │  │
│  │    Output: [{type, title, xColumn, yColumn, priority}]            │  │
│  │                                                                   │  │
│  │  KPIAgent                                                         │  │
│  │    Input: DataFrame + column_analysis                             │  │
│  │    Process:                                                       │  │
│  │      - Per numeric column: mean, median, min, max, std, sum      │  │
│  │      - Financial columns get total + average                      │  │
│  │      - Display names from semantic inference                      │  │
│  │    Output: {column_name: {mean, median, min, max, ...}}           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CHAT AGENT (LangChain)                         │  │
│  │                                                                   │  │
│  │  Model routing:                                                   │  │
│  │    messages < 10 → GPT-4o-mini (fast, cheap)                     │  │
│  │    messages >= 10 → GPT-4o (deeper reasoning)                    │  │
│  │                                                                   │  │
│  │  State: InMemorySaver checkpointer (per thread_id)               │  │
│  │  Input: user message + dataset context                            │  │
│  │  Output: analysis response + optional statistics                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Upload & Analysis Pipeline

```
User uploads file
       │
       ▼
Express receives multipart form data (Multer)
       │
       ▼
Saves to uploads/ directory
       │
       ▼
Spawns Python: bi_agent_team.py <filepath>
       │
       ├─→ Tries SuperIntelligentParser
       │     └─→ Falls back to IntelligentParser
       │           └─→ Falls back to SmartDataParserV2
       │                 └─→ Falls back to ProcessData
       │
       ▼
Parser returns structured JSON (stdout)
       │
       ▼
bi_agent_team.py creates DataFrame from parsed data
       │
       ├─→ DataStructureAgent.analyze(df)
       ├─→ VisualizationAgent.recommend(df, analysis)
       └─→ KPIAgent.generate(df, analysis)
       │
       ▼
Combined result returned as JSON
       │
       ▼
Express stores in Maps (datasets, kpis, visualizations)
       │
       ▼
Response sent to React frontend
       │
       ▼
Frontend renders KPI cards + chart tabs
       │
       ▼
For each visualization, frontend POSTs to /api/chart-data
       │
       ▼
Server generates Plotly-compatible trace data from stored dataset
       │
       ▼
Plotly.js renders interactive chart
```

### Chat Pipeline

```
User types question in chat drawer
       │
       ▼
POST /api/chat {message, datasetName, threadId}
       │
       ▼
Express spawns Python: chat_agent.py <message> <dataset> <thread>
       │
       ▼
LangChain agent processes with dynamic model selection
       │
       ▼
Response returned to frontend
       │
       ▼
Chat drawer displays AI response
```

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend framework | React 18 | Component model fits dashboard layout; Plotly.js has first-class React bindings |
| UI library | Material UI | KPI cards, tabs, drawers match BI dashboard patterns |
| Charting | Plotly.js | Interactive charts with zoom, hover, export; supports heatmaps natively |
| API server | Express.js | Lightweight; easy IPC with Python via child_process |
| AI framework | LangChain + LangGraph | Agent abstractions, model routing, conversation memory |
| LLM | OpenAI GPT-4o / GPT-4o-mini | Best reasoning for data analysis; mini for cost-effective simple queries |
| Data processing | Pandas + NumPy | Industry standard for tabular data manipulation |
| IPC protocol | JSON over stdout | Simple, debuggable; stderr used for logging without corrupting output |

## Deployment

### Docker Architecture

```
┌─────────────────────────────┐     ┌─────────────────────────────┐
│  frontend container          │     │  backend container           │
│                              │     │                              │
│  Node 18 + serve             │────▶│  Node 18 + Python 3         │
│  Static React build          │     │  Express + Pandas/NumPy     │
│  Port 3002                   │     │  Port 3001                   │
│                              │     │                              │
│                              │     │  Volume: uploads/            │
└─────────────────────────────┘     └─────────────────────────────┘
```

### Resource Requirements

- **Memory**: ~512MB minimum (Python data processing is the primary consumer)
- **CPU**: 1 core minimum; parsing and agent analysis are CPU-bound
- **Disk**: ~200MB for dependencies; uploads stored temporarily
- **Network**: Outbound HTTPS to OpenAI API (chat agent only; KPI/viz generation is fully local)
