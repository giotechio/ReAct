# Dynamic prcing agent with LLM Reasoning and External Tool call

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
import requests
from display_graph import display_graph

# Define the mock API for demand and competitor pricing
def get_demand_data(product_id:str)->dict:
    """Mock demand API to get demand data for a product"""
    # for real world replace with an actual API
    return {"product_id":product_id, "demand_level":"low"}

def get_competitor_pricing(product_id:str)->dict:
    """Mock competitor pricing API"""
    return {"product_id":product_id, "competitor_price":87.0}

# Tools list
tools = [get_demand_data, get_competitor_pricing]

#-------------------------------------
# Define Agent with ReAct pattern
# llm_model = "qwen3:1.7b"
# llm_model = "gemma4:e2b"
llm_model ="qwen3.5:2b-q4_K_M" 
model = ChatOllama(model=llm_model)

# Create ReAct agent with tools
graph = create_agent(model, tools=tools)

# Define the initial state of the agent
initial_messages = [
    ("system", "You are an AI agent that dinamically adjusts product prices based on market demand and competitor prices."),
    ("user", "What should be the price for product ID'12345'?")
]

# Stream agent responsees and decisions
inputs = {"messages":initial_messages}
# Simulate the agent reasoning, acting  and observing
for state in graph.stream(inputs, stream_mode="values"):
    message=state["messages"][-1] # get the latest message
    if isinstance(message, tuple):
        print(message)
    else:
        message.pretty_print() 

# display_graph(graph)
