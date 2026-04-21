from langchain_core.runnables.graph import MermaidDrawMethod
import os
import sys
import random
import subprocess

def display_graph(graph, output_folder="output"):
    """code to visualise the graph"""

    mermaid_png = graph.get_graph(xray=1).draw_mermaid_png(draw_method=MermaidDrawMethod.API)
    
    # create an output folder if it does not exist to save the current folder represented by '.'
    output_folder = "."
    os.makedirs(output_folder, exist_ok=True)
    
    
    filename = os.path.join(output_folder,f"graph_{random.randint(1,10000)}.png")
    with open(filename, 'wb') as f:
        f.write(mermaid_png)
        
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filename))
    if sys.platform.startswith('linux'):
        subprocess.call(('xdg-open', filename))
    if sys.platform.startswith('win'):
        subprocess.call( filename)  