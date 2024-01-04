import networkx as nx
import os
import matplotlib.pyplot as plt
from collections import Counter

def read_dimacs_graph(file_path):
    '''
        Parse .col file and return graph object
    '''
    edges = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('c'):  # graph description
                print(*line.split()[1:])
            # first line: p name num_of_vertices num_of_edges
            elif line.startswith('p'):
                p, name, vertices_num, edges_num = line.split()
                print('{0} {1} {2}'.format(name, vertices_num, edges_num))
            elif line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((v1, v2))
            else:
                continue
        return nx.Graph(edges)
    
def calculate_boundings(graph, current_clique_number):
    color_classes_ = nx.coloring.greedy_color(graph, strategy="DSATUR")

    # Get the chromatic number by finding the maximum value in the color dictionary
    chromatic_number = len(set(color_classes_.values()))
    color_classes = {}
    # Iterate through the original dictionary
    for key, value in color_classes_.items():
        if value in color_classes:
            color_classes[value].append(key)
        else:
            color_classes[value] = [key]
    color_classes = dict(sorted(color_classes.items(), key=lambda item: len(item[1])))
    
    if chromatic_number >= current_clique_number:
        max_clique = nx.approximation.max_clique(graph)
        clique_number = len(max_clique)
        if clique_number >= current_clique_number:                
            current_clique_number = clique_number
            # print(max_clique)
            if clique_number == chromatic_number:
                return chromatic_number, color_classes, current_clique_number, max_clique, True
            else:
                return chromatic_number, color_classes, current_clique_number, None, True
        else:
            return chromatic_number, color_classes, current_clique_number, None, True
    else:
        return chromatic_number, color_classes, current_clique_number, None, False
    
def choose_color_class(chromatic_number, clique_number, color_classes_, graph):
    color_classes = dict(sorted(color_classes_.items(), key=lambda item: len(item[1])))
    kclique_covering_vertex_set = []
    k = (chromatic_number - clique_number)+1
    number_vertices = graph.number_of_nodes()
    for i in range(k):
        keys_list = list(color_classes.keys())
        chosen_key = keys_list[i]
        for vertex in color_classes[chosen_key]:
            if nx.degree(graph, str(vertex)) !=( number_vertices-1):
                if len(kclique_covering_vertex_set) > 0:
                    temp = kclique_covering_vertex_set.copy()
                    for vertex1 in temp:
                        if graph.has_edge(str(vertex), vertex1) == True:
                            if vertex in kclique_covering_vertex_set:
                                kclique_covering_vertex_set.remove(vertex)
                            else:    
                                continue
                        else:
                            if vertex not in kclique_covering_vertex_set:
                                kclique_covering_vertex_set.append(vertex)
                else:
                    kclique_covering_vertex_set.append(vertex)
    kclique_covering_vertex_set_sorted = sorted(kclique_covering_vertex_set, key=lambda x: nx.degree(graph, x), reverse=True)
    return kclique_covering_vertex_set_sorted

def branching(kclique_covering_vertex_set, graph):
    subgraphs = []
    for vertex in kclique_covering_vertex_set:
        neighbors = list(graph.neighbors(vertex))

        # Include the chosen vertex and its neighbors in the subgraph
        subgraph_nodes = [vertex] + neighbors
        subgraph = graph.subgraph(subgraph_nodes)
        subgraphs.append(subgraph)
    return subgraphs

# graph = read_dimacs_graph("samples/le450_15c.col")
# graph = read_dimacs_graph("D:\Python\max_clique\samples\le450_25d.col")
graph = read_dimacs_graph("samples/anna.col")
# graph = read_dimacs_graph("clq/brock200_1.clq.txt")
# graph = read_dimacs_graph("clq/C125.9.clq.txt")

subgraphs = []
kclique_covering_node_set = []
wG = 0
max_cliques = []
xG, colorClass, wG_, max_clique, branch = calculate_boundings(graph, wG)
if wG_ > wG:
    max_cliques = []
    wG = wG_
if max_clique is not None:
    max_cliques.append(max_clique)
kclique_covering_node_set = choose_color_class(xG, wG, colorClass, graph)
subgraphs = branching(kclique_covering_node_set, graph)
print("clique number", wG, " | subgraphs", len(subgraphs), " | chromatic number", xG , " | branch", branch)
find = True

while find:
    xG, colorClass, wG_, max_clique, branch = calculate_boundings(subgraphs[0], wG)
    if wG_ > wG:
        max_cliques = []
        wG = wG_
    if max_clique is not None:
        max_cliques.append(max_clique)
    print("clique number", wG, " | subgraphs", len(subgraphs), " | chromatic number", xG , " | branch", branch)
    if branch:
        kclique_covering_node_set = choose_color_class(xG, wG, colorClass, subgraphs[0])
        subgraphs = subgraphs + branching(kclique_covering_node_set, subgraphs[0])
    subgraphs.remove(subgraphs[0])
    if len(subgraphs) == 0:
        find = False
        
print("[FINISH]")
print(f"clique number: {wG}")
print("[list maximum cliques]")
print(max_cliques)