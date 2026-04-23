# Sentiment Analysis Agent with LLM and Custom tools

from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# Define the state for the agent
class AgentState(TypedDict):
    """The state for the agent"""
    messages:Annotated[Sequence[BaseMessage],add_messages]

# Sentiment Analysis tool

from langchain_core.tools import tool
from textblob import TextBlob

@tool
def analyze_sentiment(feedback:str)->str:
    """ """
    analysis  = TextBlob(feedback)
    if analysis.sentiment.polarity > 0.5:
        return "positive"
    elif analysis.sentiment.polarity == 0.5:
        return "neutral"
    else:
        return "negative"


# ----------------------------
# response genaration tool
@tool
def respond_based_on_sentiment(sentiment:str)->str:
    """  """
    if sentiment == "positive":
        return "Thank you for your positive feedback!"
    elif sentiment == "neutral":
        return "We appreciate your feedback."
    else:
        return "We're sorry to hear that you're not satisfied. How can we help?"
# ------------------------------
# Tools for LLM
from langchain_ollama import ChatOllama
from langchain_core.messages import ToolMessage, SystemMessage
tools = [analyze_sentiment, respond_based_on_sentiment]
# Initialize the LLM
# llm_model = "qwen3:1.7b"
# llm_model = "gemma4:e2b"
llm_model ="qwen3.5:2b-q4_K_M" 
llm = ChatOllama(model=llm_model)
llm = llm.bind_tools(tools)
# Create a dictionary of tools by their names for easy lookup
tools_by_name = {tool.name: tool for tool in tools}

# ---------------------------------
# define tool executiopn node
import json
from langchain_core.messages import ToolMessage
# Tool node to handle sentiment analysis and response generation
def tool_node(state: AgentState):
    outputs = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}

# -------------------------------
# LLM reasoning Node
from langchain_core.runnables import RunnableConfig
# LLM reasoning node to process the feedback and call tools if needed
def call_model(state: AgentState, config: RunnableConfig):
    system_prompt = SystemMessage(
        content="You are a helpful assistant tasked with responding to customer feedback."
    )
    response = llm.invoke([system_prompt] + state["messages"], config)
    return {"messages": [response]}


# -------------------------
# define state transitions
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"

# --------------------------------
# build stategraph
from langgraph.graph import StateGraph, START, END
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END,
    },
)
workflow.add_edge("tools", "agent")
# Compile the graph
graph = workflow.compile()

#------------
# visdualize
from display_graph import display_graph
display_graph(graph)

#------------
# initialize the graph and run
# Initialize the agent's state with the user's feedback
initial_state = {"messages": [("user", "The product was great but the delivery was poor.")]}
# Helper function to print the conversation
def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()
# Run the agent
print_stream(graph.stream(initial_state, stream_mode="values"))