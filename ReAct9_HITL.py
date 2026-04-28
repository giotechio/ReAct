import os
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from display_graph import display_graph

# Set up your LLM

llm_model = "qwen3:1.7b"
# llm_model = "gemma4:e2b"
# llm_model ="qwen3.5:2b-q4_K_M" 
model = ChatOllama(model=llm_model)
# Initialize the model
llm = ChatOllama(
    model=llm_model,     # Specify the model
    temperature=0.7,    # Adjust for creativity in output
    max_tokens=50    # Set maximum token length for responses
)

# Define the state structure
class State(TypedDict):
    input: str
    draft_content: str
# Define node functions
def create_draft(state: State):
    print("--- Generating Draft with ChatOllama ---")
# Prepare the prompt for generating the blog content
    prompt = f"Write a blog post on the topic: {state['input']}"
# Call the LangChain ChatOllama instance to generate the draft
    response = llm.invoke([{"role": "user", "content": prompt}])
# Extract the generated content
    state["draft_content"] = response.content
    print(f"Generated Draft:\n{state['draft_content']}")
    return state
def review_draft(state: State):
    print("--- Reviewing Draft ---")
    print(f"Draft for review:\n{state['draft_content']}")
    return state
def publish_content(state: State):
    print("--- Publishing Content ---")
    print(f"Published Content:\n{state['draft_content']}")
    return state

# Build the graph
builder = StateGraph(State)
builder.add_node("create_draft", create_draft)
builder.add_node("review_draft", review_draft)
builder.add_node("publish_content", publish_content)
# Define flow
builder.add_edge(START, "create_draft")
builder.add_edge("create_draft", "review_draft")
builder.add_edge("review_draft", "publish_content")
builder.add_edge("publish_content", END)
# Set up memory and breakpoints
memory = MemorySaver()

graph = builder.compile(checkpointer=memory, interrupt_before=["publish_content"])
# Display the graph
# # display_graph(graph)#, file_name=os.path.basename(__file__))
# Run the graph
config = {"configurable": {"thread_id": "thread-1"}}
initial_input = {"input": "The importance of AI in modern content creation"}
# Run the first part until the review step
thread = {"configurable": {"thread_id": "1"}}
for event in graph.stream(initial_input, thread, stream_mode="values"):
    print(event)
    # Pausing for human review
user_approval = input("Do you approve the draft for publishing? (yes/no/modification):")

if user_approval.lower() == "yes":
# Proceed to publish content
    for event in graph.stream(None, thread, stream_mode="values"):
        print(event)
elif user_approval.lower() == "modification":
# Allow modification of the draft
    updated_draft = input("Please modify the draft content:\n")
    memory.update({"draft_content": updated_draft})
 # Update memory with new
    content
    print("Draft updated by the editor.")
# Continue to publishing with the modified draft
    for event in graph.stream(None, thread, stream_mode="values"):
        print(event)
else:
    print("Execution halted by user.")
    if user_approval.lower() == "yes":
# Proceed to publish content
        for event in graph.stream(None, thread, stream_mode="values"):
            print(event)
    elif user_approval.lower() == "modification":
# Allow modification of the draft
        updated_draft = input("Please modify the draft content:\n")
        memory.update({"draft_content": updated_draft})
 # Update memory with new content
        print("Draft updated by the editor.")
# Continue to publishing with the modified draft
        for event in graph.stream(None, thread, stream_mode="values"):
            print(event)
    else:
        print("Execution halted by user.")