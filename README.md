
# Game Theory #
Sarah Hooper 032031049

Due Date: October 21, 2025

## Usage ##
### Create Virtual Environment and Install Dependencies ##
` python3 -m venv venv`

`source venv/bin/activate`

`pip install networkx matplotlib numpy scipy`

### Running Program ###
`python traffic_analysis.py <gml file> <num_vehicles> <start_node> <end_node> --plot`

## Implementation ##
### Core Functions ###

**parse_args()** -> Parses command-line arguments

**load_graph()** ->	Loads and validates the GML file as a directed graph

**get_all_paths()** ->	Finds all simple paths between start and end nodes

**assign_flow_social_optimum()** ->	Uses constrained optimization to minimize total system cost

* Define a function total_cost(flow_split) that:

  * Initializes flow on all edges to 0.

  * For each path and proposed flow f, adds that flow to every edge on the path.

  * Computes the total system cost by summing x * (a*x + b) over all edges.

* Use scipy.optimize.minimize() to solve

**assign_flows_nash_equilibrium()** ->	This distributes vehicles equally among all available paths.

**flows_to_edge_flows()** ->	Combines path-level flows to edge-level

**compute_social_cost()** ->	Calculates total travel time across all edges

**plot_graph()** ->	Visualizes the graph with flow and cost annotations
