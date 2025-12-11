# Data Visualization & Analysis Platform

A production-ready data visualization and analysis platform with AI-powered insights, built with React frontend and Node.js/Python backend.

## Features

- **Smart Data Parsing**: Automatically understands complex Excel structures and summary formats
- **BI Agent Team**: Multi-agent system for deep data analysis
- **Meaningful KPIs**: Automatically generates contextual KPIs with descriptive names
- **Interactive Visualizations**: Dynamic charts and graphs using Plotly.js
- **AI Chat Interface**: Chat with your data using LangChain agents

## Architecture

```
LangChain/
├── backend/              # Node.js + Python backend
│   ├── server.js        # Express API server
│   ├── bi_agent_team.py # BI analysis agents
│   ├── smart_data_parser_v2.py # Smart data parser
│   ├── process_data.py  # Data processing
│   ├── get_chart_data.py # Chart data extraction
│   └── chat_agent.py    # Chat interface
├── frontend/            # React frontend
│   └── src/
│       └── App.js       # Main React component
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Setup

### Prerequisites
- Node.js 16+
- Python 3.10+
- npm or yarn

### Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install backend dependencies:**
```bash
cd backend
npm install
```

3. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

4. **Set up environment variables:**
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_key
NOMIC_API_KEY=your_nomic_key
PORT=3002
```

## Running the Application

### Start Backend (Port 3001)
```bash
cd backend
node server.js
```

### Start Frontend (Port 3002)
```bash
cd frontend
npm start
```

The application will be available at `http://localhost:3002`

## Usage

1. **Upload Data**: Upload CSV, Excel, or JSON files through the web interface
2. **View KPIs**: Automatically generated KPIs with meaningful names
3. **Explore Visualizations**: Interactive charts and graphs
4. **Chat with Data**: Use the chat interface to ask questions about your data

## BI Agent Team

The system uses a multi-agent approach for data analysis:

- **DataStructureAgent**: Understands data structure and infers column meanings
- **VisualizationAgent**: Recommends appropriate visualizations
- **KPIAgent**: Generates meaningful KPIs with proper context

See `BI_AGENT_TEAM.md` for detailed documentation.

## Technology Stack

- **Frontend**: React, Material-UI, Plotly.js
- **Backend**: Node.js (Express), Python (Pandas, NumPy)
- **AI**: LangChain, OpenAI
- **Data Processing**: Pandas, NumPy

## License

MIT
