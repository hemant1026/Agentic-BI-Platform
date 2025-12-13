# 📊 LangChain Data Visualization & Analysis Platform

![React](https://img.shields.io/badge/React-18-blue) ![Node.js](https://img.shields.io/badge/Node.js-16+-green) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![LangChain](https://img.shields.io/badge/LangChain-AI-orange)

**AI-powered full-stack data analysis platform with multi-agent BI system and interactive visualizations**

---

## 📖 Overview

Production-ready data visualization and analysis platform that combines React frontend with Node.js/Python backend to deliver AI-powered insights. Features include smart data parsing, multi-agent BI analysis, automatic KPI generation, and conversational data exploration using LangChain.

## ✨ Key Features

### 🤖 Multi-Agent BI System
- **Intelligent Analysis**: Team of specialized AI agents for deep data insights
- **Contextual KPIs**: Auto-generated metrics with business-relevant names
- **Pattern Recognition**: Automatic trend and anomaly detection

### 📈 Interactive Visualizations
- **Plotly.js Integration**: Dynamic, interactive charts
- **Multiple Chart Types**: Line, bar, scatter, heatmap, and more
- **Real-time Updates**: Live data visualization

### 💬 AI Chat Interface
- **Natural Language Queries**: Ask questions in plain English
- **Contextual Responses**: AI understands your data context
- **LangChain Powered**: Advanced conversational AI capabilities

### 📁 Smart Data Processing
- **Format Agnostic**: Handles CSV, Excel, JSON
- **Complex Structures**: Parses nested and summary formats
- **Data Validation**: Automatic quality checks

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.10+
- OpenAI API key

### Installation

```bash
# Clone repository
git clone https://github.com/hemant1026/LangChain.git
cd LangChain

# Install Python dependencies
pip install -r requirements.txt

# Install backend dependencies
cd backend && npm install && cd ..

# Install frontend dependencies
cd frontend && npm install && cd ..

# Configure environment
echo "OPENAI_API_KEY=your_key
NOMIC_API_KEY=your_key  
PORT=3002" > .env
```

### Run Application

```bash
# Terminal 1: Start backend (Port 3001)
cd backend && node server.js

# Terminal 2: Start frontend (Port 3002)
cd frontend && npm start
```

Access at: http://localhost:3002

## 💻 Tech Stack

**Frontend**: React 18, Plotly.js, Axios
**Backend**: Node.js, Express
**AI/ML**: Python, LangChain, OpenAI GPT-4, Pandas, NumPy
**Data Viz**: Plotly, D3.js

## 🏗️ Architecture

```
Frontend (React) ← HTTP → Backend (Express) ← IPC → Python Agents
     ↓                            ↓                        ↓
   UI/UX              API Gateway            AI Processing
```

## 👨‍💻 Author

**Hemant Krishnakumar**
- GitHub: [@hemant1026](https://github.com/hemant1026)
- Email: hemant1026@gmail.com

---

⭐ Star this repository if you find it helpful!
