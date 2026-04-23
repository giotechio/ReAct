# ReAct multi-step reasoning , Dynamic sub-graphs
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict
from display_graph import display_graph

class ReActAgentState(TypedDict):
    message:str
    action:str
    sub_action:str

# Reasoning Node1 : Determines which action the agent should perform
def reasoning_node(state:ReActAgentState):
    query = state["message"]
    if "weather" in query:
        return{"action":"fetch_weather"}
    elif "news" in query:
        return {"action":"fetch_news"}
    elif "recommend" in query:
        return {"action":"recommendation", "sub_action":"book"}
    else:
        return {"action":"unknown"}

# Sub-graph for fetching weather information(acting phase)
def weather_subgraph_node(state:ReActAgentState):
    return {"message": "The weather today is sunny."}

# Sub-graph for fetching NEWS information(acting phase)
def news_subgraph_node(state:ReActAgentState):
    return {"message": "Here are the latest news headlines"}

# Sub-graph for book recommendation(acting phase)
def recommendation_subgraph_node(state:ReActAgentState):
    if state.get("sub_action") == "book":
        return {"message": "I recommend reading 'The Pragmatic Programmer'."}
    else:
        return{"message":"I have no other recommendationns at the momennt"}

# Build sub-graph for fetching weather info

weather_subgraph_workflow = StateGraph(ReActAgentState)
weather_subgraph_workflow.add_node("weather_action", weather_subgraph_node)
weather_subgraph_workflow.set_entry_point("weather_action")
weather_subgraph = weather_subgraph_workflow.compile()

# Build sub-graph for fetching NEWS info

news_subgraph_workflow = StateGraph(ReActAgentState)
news_subgraph_workflow.add_node("news_action", news_subgraph_node)
news_subgraph_workflow.set_entry_point("news_action")
news_subgraph = news_subgraph_workflow.compile()

# Build sub-graph for recommendation

recommendation_subgraph_workflow = StateGraph(ReActAgentState)
recommendation_subgraph_workflow.add_node("recommendation_action", recommendation_subgraph_node)
recommendation_subgraph_workflow.set_entry_point("recommendation_action")
recommendation_subgraph = recommendation_subgraph_workflow.compile()

# Definne dynamic reasoninng node in the parent graph t oroute to the correct subgraph

def reasoning_state_manager(state:ReActAgentState):
    if state["action"] =="fetch_weather":
        return weather_subgraph
    elif state["action"] == "fetch_news":
        return news_subgraph
    elif state["action"] =="recommendation":
        return recommendation_subgraph
    else:
        return None
# Create the Parent graph
parent_workflow = StateGraph(ReActAgentState)
parent_workflow.add_node("reasoning", reasoning_node)
parent_workflow.add_node("action_dispatch", reasoning_state_manager)

# Define edges in parent graph
parent_workflow.add_edge(START, "reasoning")
parent_workflow.add_edge("reasoning","action_dispatch")

# Compile the graph
react_agent_graph = parent_workflow.compile()

# Test the agent with weather related query
inputs_weather = {"message":"What is the weather today?"}
result_weather = react_agent_graph.invoke(inputs_weather)

# Test the agent with NEWS related query
inputs_news = {"message":"Give me the latest news"}
result_news = react_agent_graph.invoke(inputs_news)

# Test the agent with recommendation related query
inputs_recommendation = {"message":"Can you recommend me a book?"}
result_recommendation = react_agent_graph.invoke(inputs_recommendation)

print(result_weather["message"])
print(result_news["message"])
print(result_recommendation["message"])

display_graph(react_agent_graph)