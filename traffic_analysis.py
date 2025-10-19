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


def plot_graph(G, edge_flows, title="Graph", social_cost=None, potential_power=None, start=None, end=None):
    nodes = list(G.nodes())
    middle_nodes = [n for n in nodes if n != start and n != end]
    ordered_nodes = [start] + sorted(middle_nodes) + [end]
    x_spacing = 2.5
    y_spacing = 2
    pos = {}
    pos[start] = (0, 0)

    for i, node in enumerate(sorted(middle_nodes)):
        x = (i + 1) * x_spacing
        y = y_spacing if i % 2 == 0 else -y_spacing
        pos[node] = (x, y)

    pos[end] = ((len(ordered_nodes) - 1) * x_spacing, 0)

    plt.figure(figsize=(10, 5))
    nx.draw(G, pos, with_labels=True, node_size=1000, node_color='steelblue', font_color='white', arrows=True)

    edge_labels = {}
    total_potential = 0
    for (u, v) in G.edges():
        a = G[u][v].get("a", 0)
        b = G[u][v].get("b", 0)
        x = edge_flows.get((u, v), 0)
        travel_time = a * x + b
        potential = x * travel_time
        total_potential += potential

        label = f"{a}x + {b}, Drivers {x:.0f}\nTravel Time {travel_time:.0f}\nPotential Power {int(potential)}"
        edge_labels[(u, v)] = label

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=9)

    # Add total cost as text
    info_lines = []
    if title is "Nash Equilibrium":
        info_lines.append(f"Nash equilibrium")
    if title is "Social Optimum":
        info_lines.append(f"Social Optimum")
    if social_cost is not None:
        info_lines.append(f"Social Cost {int(social_cost)}")
    if potential_power is not None:
        info_lines.append(f"Potential power {int(potential_power)}")
    elif total_potential:
        info_lines.append(f"Potential power {int(total_potential)}")

    plt.text(0.05, 0.01, "\n".join(info_lines), transform=plt.gca().transAxes, fontsize=10, color='black')
    plt.title(title)
    plt.tight_layout()
    plt.show()


def compute_social_cost(edge_flows, G):
    total = 0
    for (u, v), x in edge_flows.items():
        a = G[u][v].get("a", 0)
        b = G[u][v].get("b", 0)
        total += x * (a * x + b)
    return total


def main():
    args = parse_args()
    G = load_graph(args.gml_file)

    start = str(args.start)
    end = str(args.end)

    print("graph nodes:", G.nodes)
    paths = get_all_paths(G, start, end)
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
        plot_graph(G, nash_edge_flows, title="Nash Equilibrium", social_cost=compute_social_cost(nash_edge_flows, G),
                   start=start, end=end)
        plot_graph(G, opt_edge_flows, title="Social Optimum", social_cost=compute_social_cost(opt_edge_flows, G),
                   start=start, end=end)


if __name__ == "__main__":
    main()



