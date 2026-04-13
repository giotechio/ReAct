from langchain_ollama import ChatOllama
from langchain.agents import create_agent

# Define tools
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b
tools = [add, multiply]
# Initialize the LLM

llm = ChatOllama(model="qwen3:1.7b")
# Create the ReAct agent
graph = create_agent(model=llm, tools=tools)
# User input
inputs = {"messages": [("user", "Add 3 and 4. Multiply the result by 2.")]}
# Run the ReAct agent
messages = graph.invoke(inputs)
for message in messages["messages"]:
    print(message.content)