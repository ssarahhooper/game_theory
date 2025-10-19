import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize


def parse_args():
    parser = argparse.ArgumentParser(description="Traffic flow equilibrium and social optimum calculator")
    parser.add_argument("gml_file", type=str, help="Path to GML file")
    parser.add_argument("vehicles", type=int, help="Number of vehicles")
    parser.add_argument("start", type=int, help="Start node")
    parser.add_argument("end", type=int, help="End node")
    parser.add_argument("--plot", action="store_true", help="Plot the graph")
    return parser.parse_args()


def load_graph(path):
    try:
        G = nx.read_gml(path)
        if not nx.is_directed(G):
            raise ValueError("Graph is not directed")
        return G
    except Exception as e:
        print(f"Error loading graph: {e}")
        exit(1)


def get_all_paths(G, start, end):
    return list(nx.all_simple_paths(G, source=start, target=end))


# distribute vechicles across multiple paths from a source to a destination, so total cost across whole
# network is minimized
def assign_flow_social_optimum(G, paths, n):
    # compute the total system cost given proposed distrubution
    def total_cost(flow_split):
        # initalize flow on every edge to 0
        edge_flows = {(u, v): 0 for u, v in G.edges()}
        # loop through each path and proposed flow
        for f, path in zip(flow_split, paths):
            for i in range(len(path) - 1):
                # for each edge in path add flow to that edge's total flow
                u, v = path[i], path[i + 1]
                edge_flows[(u, v)] += f
        total = 0
        # compute total system cost
        # each edge gets flow x
        for (u, v), x in edge_flows.items():
            a = G[u][v].get("a", 0)
            b = G[u][v].get("b", 0)
            # copmpute edge cost per vehicle and multiply by total flow
            total += x * (a * x + b)
        return total

    # create inital guess
    x0 = np.ones(len(paths)) * (n/len(paths))
    # create bounds so no path can have more than n cars
    bounds = [(0, n)] * len(paths)
    # sum of all paths must equal n vechiles
    cons = ({'type': 'eq', 'fun': lambda x: sum(x) - n})
    # use minimize to find path flows that minimize total cost
    res = minimize(total_cost, x0, bounds=bounds, constraints=cons)
    return res.x if res.success else None





