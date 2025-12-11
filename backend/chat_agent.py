#!/usr/bin/env python3
"""
Chat agent interface for data visualization
"""
import sys
import json
import os
from dotenv import load_dotenv

# Add parent directory to path to import agent
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Import agent components
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.tools import tool, ToolRuntime
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

@dataclass
class Context:
    user_id: str
    current_dataset: str = None

@dataclass
class ResponseFormat:
    analysis_response: str
    visualization_description: str | None = None
    key_statistics: str | None = None
    recommendations: str | None = None

# Initialize agent (simplified for API use)
basic_model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, timeout=30, max_tokens=2000)
advanced_model = ChatOpenAI(model="gpt-4o", temperature=0.7, timeout=30, max_tokens=2000)

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    message_count = len(request.state.get("messages", []))
    request.model = advanced_model if message_count > 10 else basic_model
    return handler(request)

checkpointer = InMemorySaver()

# Note: This is a simplified version - in production, you'd want to cache the agent
# For now, we'll return a simple response
def chat_with_agent(message, dataset_name, thread_id):
    try:
        result = {
            'response': f"Analysis for {dataset_name}: {message}",
            'key_statistics': None,
            'recommendations': None
        }
        print(json.dumps(result))
        return result
    except Exception as e:
        error_result = {'error': str(e)}
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(json.dumps({'error': 'Missing arguments'}))
        sys.exit(1)
    
    message = sys.argv[1]
    dataset_name = sys.argv[2]
    thread_id = sys.argv[3]
    chat_with_agent(message, dataset_name, thread_id)

