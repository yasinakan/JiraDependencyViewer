import csv
from io import StringIO
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np



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


def read_task_dependencies(filepath):
    """Read task dependencies from CSV file and return content as string."""
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return ""
    except Exception as e:
        print(f"Error reading file: {e}")
        return ""


def parse_tasks(content):
    """Parse CSV content and return list of tasks and their dependencies.
    If task1 is blocked by task2, creates an edge from task2 to task1"""
    tasks = set()
    dependencies = []
    csv_reader = csv.reader(StringIO(content))
    for row in csv_reader:
        # Skip empty rows
        if not row:
            continue
        # The first task is blocked by the following tasks
        blocked_task = row[0]
        for blocking_task in row[1:]:
            if blocking_task:  # Only add if blocking_task is not empty
                tasks.add(blocking_task)
                tasks.add(blocked_task)
                # Create edge from blocking task to blocked task
                dependencies.append((blocking_task, blocked_task))
    return sorted(list(tasks)), dependencies

def main():
    content = read_task_dependencies('doc/Isblockedby.csv')
    tasks, dependencies = parse_tasks(content)
    sprint_data = read_sprints('doc/Sprints.csv')

    dependenciesWithSprints = []
    task_sprint_map = {}  # For quick sprint number lookup
    # Create a mapping of tasks to their sprint information
    for task in tasks:
        if task in sprint_data:
            sprint, sprint_num = sprint_data[task]
        else:
            sprint, sprint_num = "Future Implementation", 999
        dependenciesWithSprints.append((task, sprint, sprint_num))
        task_sprint_map[task] = sprint_num

    # Create a directed graph from the dependencies
    G = nx.DiGraph()
    G.add_edges_from(dependencies)
    
    # Identify problematic edges (earlier sprint blocked by later sprint)
    red_edges = []
    black_edges = []
    for source, target in G.edges():
        source_sprint = task_sprint_map.get(source, -1)
        target_sprint = task_sprint_map.get(target, -1)
        if target_sprint != -1 and source_sprint > target_sprint:
            red_edges.append((source, target))
        else:
            black_edges.append((source, target))

    # Draw the graph
    plt.figure(figsize=(15, 8))
    
    # Create custom layout based on sprint numbers
    pos = {}
    all_sprints = sorted(list(set(task_sprint_map.values())))
    sprint_to_x = {sprint: idx for idx, sprint in enumerate(all_sprints)}
    
    # Group tasks by sprint
    tasks_by_sprint = {}
    for task, sprint_num in task_sprint_map.items():
        if sprint_num not in tasks_by_sprint:
            tasks_by_sprint[sprint_num] = []
        tasks_by_sprint[sprint_num].append(task)
    
    # Position nodes
    for sprint_num, tasks in tasks_by_sprint.items():
        x = sprint_to_x[sprint_num]
        for i, task in enumerate(tasks):
            y = i - len(tasks)/2
            pos[task] = (x, y)
    
    # Draw regular edges in black
    nx.draw_networkx_edges(G, pos, edgelist=black_edges, edge_color='black', arrows=True)
    
    # Draw problematic edges in red with increased width
    nx.draw_networkx_edges(G, pos, edgelist=red_edges, edge_color='red', arrows=True, width=2)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=2000, node_color='lightblue')
    nx.draw_networkx_labels(G, pos, font_size=10)
    
    # Add edge labels for problematic dependencies
    edge_labels = {(s,t): "Is blocked by" for (s,t) in red_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')
    
    plt.title("Task Dependencies (Red = Task blocked by later sprint)")

    # Annotate nodes with sprint information
    for task, sprint, sprint_num in dependenciesWithSprints:
        if task in pos:
            plt.annotate(sprint, xy=pos[task], textcoords="offset points", xytext=(0,10), ha='center')
    plt.show()

    # Print problematic dependencies
    if red_edges:
        print("\nProblematic Dependencies (Tasks blocked by later sprints):")
        print("-" * 60)
        for source, target in red_edges:
            source_sprint = sprint_data.get(source, ("Future Implementation", -1))[0]
            target_sprint = sprint_data.get(target, ("Future Implementation", -1))[0]
            print(f"• {target} ({target_sprint}) is blocked by {source} ({source_sprint})")
    else:
        print("No problematic dependencies found.")




if __name__ == "__main__":
    main()
