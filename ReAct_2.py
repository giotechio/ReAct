# ReAct agent with single-thread memory

from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from display_graph import display_graph

# Define tools
def product_info(product_name: str)->str:
    """Fethch product information"""
    product_catalog = {
        "iPhone 20": "The latest iphone features an A20 chip and improved camera",
        "MacBook":"The new MacBook has M6 chip and a 14.5-inch Retina display",
    }
    return product_catalog.get(product_name, "Sorry , prduct not found.") # with default reply

# initialize the memory saver for single-thread memory
checkpointer = MemorySaver()
#initialize the LLM
llm = ChatOllama(model="qwen3:1.7b")
# Create the React agent with memory saver
graph = create_agent(model=llm, tools=[product_info], checkpointer=checkpointer)
# Set up thread configuraiton to simulate memory
config = {"configurable":{"thread_id":"thread-1"}}
# User input: Initial enquiry
inputs = {"messages":[("user", "Hi, I am Joan. Tell me about the iPhone 20.")]}
messages = graph.invoke(inputs, config=config)
for message in messages["messages"]:
    message.pretty_print()

# User input: repeated inquiry(memory recall)
inputs2 = {"messages":[("user", "Tell me more about the phone.")]}
messages2 = graph.invoke(inputs2, config=config)
for message in messages2["messages"]:
    message.pretty_print()

display_graph(graph)