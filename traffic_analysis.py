import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


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
    return list(nx.all_simple_paths(G, start, end))


