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


def assign_flows_nash_equilibrium(G, paths, n):
    # Placeholder: simple equal distribution as approximation
    return np.ones(len(paths)) * (n / len(paths))


def flows_to_edge_flows(G, paths, flows):
    edge_flows = {(u, v): 0 for u, v in G.edges()}
    for f, path in zip(flows, paths):
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            edge_flows[(u, v)] += f
    return edge_flows

def print_flows(title, edge_flows):
    print(f"\n{title}")
    for (u, v), f in edge_flows.items():
        print(f"Edge ({u} -> {v}: {f:.2f} vehicles")


def plot_graph(G):
    pos = nx.spring_layout(G)
    edge_labels = {(u, v): f"{G[u][v].get('a', 0)}x+{G[u][v].get('b', 0)}" for u, v in G.edges()}
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', arrows=True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Traffic Network with Edge Cost Functions")
    plt.show()


def main():
    args = parse_args()
    G = load_graph(args.gml_file)
    paths = get_all_paths(G, args.start, args.end)
    if not paths:
        print("No path found")
        return

    n = args.vehicles

    # compute Nash and optimal flows
    # nash find equal distribution
    nash_flows = assign_flows_nash_equilibrium(G, paths, n)
    # social optimization
    opt_flows = assign_flow_social_optimum(G, paths, n)

    # converts path level flows to edge level flows
    nash_edge_flows = flows_to_edge_flows(G, paths, nash_flows)
    opt_edge_flows = flows_to_edge_flows(G, paths, opt_flows)

    # print results
    print_flows("Nash Equilibrium", nash_edge_flows)
    print_flows("Social Optimum", opt_edge_flows)

    if args.plot:
        plot_graph(G)


if __name__ == "__main__":
    main()



