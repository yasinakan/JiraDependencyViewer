import csv
from io import StringIO
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


def csv_to_matrix(content):
    """Convert CSV content to a matrix."""
    matrix = []
    csv_reader = csv.reader(StringIO(content))
    for row in csv_reader:
        matrix.append(row)
    return matrix


def read_sprints(file_path):
    """Read sprint information from CSV file."""
    sprint_map = {}
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) >= 2:
                task_id, sprint = row
                # Extract sprint number for comparison
                sprint_num = int(sprint.replace("SP", ""))
                sprint_map[task_id] = (sprint, sprint_num)
    return sprint_map


def visualize_dependencies(matrix, sprint_map):
    """Create a directed graph visualization of task dependencies with sprint information."""
    G = nx.DiGraph()
    
    # Process each column in the matrix
    for column in matrix:
        if len(column) < 1:
            continue
        task = column[0]
        # Add node with sprint information
        sprint_info = sprint_map.get(task, ("No Sprint", 0))
        G.add_node(task, sprint=sprint_info[0], sprint_num=sprint_info[1])
        
        # Add edges from blocking tasks to the main task
        for blocking_task in column[1:]:
            if blocking_task:
                G.add_edge(blocking_task, task)
    
    # Create the visualization with different colors per sprint
    plt.figure(figsize=(15, 8))
    
    # Create custom layout based on sprint numbers
    pos = {}
    
    # Group nodes by sprint
    nodes_by_sprint = {}
    for node, attrs in G.nodes(data=True):
        sprint_num = attrs.get('sprint_num', 0)  # Use get() with default value
        if sprint_num not in nodes_by_sprint:
            nodes_by_sprint[sprint_num] = []
        nodes_by_sprint[sprint_num].append(node)
    
    # Calculate max sprint number
    max_sprint = max(nodes_by_sprint.keys()) if nodes_by_sprint else 0
    
    # Position nodes from left to right based on sprint
    for sprint_num in sorted(nodes_by_sprint.keys()):
        nodes = nodes_by_sprint[sprint_num]
        x = sprint_num / (max_sprint + 1) if max_sprint > 0 else 0  # Normalize x position
        for i, node in enumerate(nodes):
            y = (i + 1) / (len(nodes) + 1)  # Space nodes vertically within their sprint column
            pos[node] = (x, y)
    
    # Get unique sprints for coloring (excluding sprint numbers)
    sprints = list(set(data[0] for data in sprint_map.values()))
    if "No Sprint" not in sprints:
        sprints.append("No Sprint")
    colors = plt.cm.Set3(np.linspace(0, 1, len(sprints)))
    sprint_color_map = dict(zip(sprints, colors))
      # Draw nodes colored by sprint
    for sprint in sprints:
        sprint_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('sprint', "No Sprint") == sprint]
        if sprint_nodes:
            nx.draw_networkx_nodes(G, pos, nodelist=sprint_nodes, 
                                 node_color=[sprint_color_map[sprint]], 
                                 node_size=2000, label=sprint)
    
    # Draw edges with different colors based on sprint order
    edges = G.edges()
    red_edges = []
    black_edges = []
    for edge in edges:
        source_sprint = G.nodes[edge[0]].get('sprint_num', 0)
        target_sprint = G.nodes[edge[1]].get('sprint_num', 0)
        if source_sprint > target_sprint and source_sprint != 0 and target_sprint != 0:
            red_edges.append(edge)
        else:
            black_edges.append(edge)
    
    # Draw regular dependencies in black
    nx.draw_networkx_edges(G, pos, edgelist=black_edges, edge_color='black', arrowsize=20)
    # Draw problematic dependencies in red
    nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', arrowsize=20)
      # Create labels with sprint information
    labels = {}
    for node in G.nodes():
        sprint_info = G.nodes[node].get('sprint', "No Sprint")
        labels[node] = f"{node}\n({sprint_info})"
    
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    plt.title("Task Dependencies by Sprint\nRed arrows indicate blocking tasks in later sprints")
    plt.legend()
    plt.show()


def main():
    content = read_file('doc/HasDependenyList.csv')
    sprint_data = read_sprints('doc/Sprints.csv')
    matrix = csv_to_matrix(content)
    visualize_dependencies(matrix, sprint_data)


def read_file(file_path):
    """Read the content of a file and return it."""
    with open(file_path, 'r') as file:
        return file.read()


if __name__ == "__main__":
    main()
