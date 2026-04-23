# Complex ReAct agent
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from display_graph import display_graph

# define tools
def product_info(product_name:str)->str:
    """Fetch product information."""
    product_catalog = {
        "Toyota Xudos":"The most recent and popular sedan with hybrid drive system",
        "Canon r5":"The most advandced photo camera features 45 megapixel sensor",
    }

    return product_catalog.get(product_name, "Sorry product not found.")

def check_stock(product_name:str)->str:
    """Check product stock availability"""
    stock_data={
        "Toyota Xudos":"In stock - 46 units.",
        "Canon-r5":"Out of stock",
    }
    return stock_data.get(product_name, "Stock information unavailable.")

# Initialize the memory saver for single-thread memory
checkpointer = MemorySaver()

# Initialize LLM
# llm_model = "qwen3.5:2b-q4_K_M"
llm_model = "gemma4:e2b"
llm = ChatOllama(model=llm_model)

# Create REACT agent with tools and memory
tools = [product_info, check_stock]

graph = create_agent(model=llm, tools=tools, checkpointer=checkpointer)

# Set  up thread configuration for single thread memory
config = {"configurable":{"thread_id":"thread-3"}}

# User input: initial inquiry about the product
inputs = {"messages": [("user", "Tell me about the Canon-r5.")]}
messages = graph.invoke(inputs, config=config)
for message in messages["messages"]:
    print (message.content)

# user input: follow up question about stock availability
inputs2 = {"messages": [("user", "Is Canon-r5 in stock?")]}
messages2 = graph.invoke(inputs2, config=config)
for message in messages2["messages"]:
    print (message.content)

# display_graph(graph)