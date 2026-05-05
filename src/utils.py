# src/utils.py
import json
import networkx as nx
import gurobipy as gp
from gurobipy import GRB

def load_instance(filepath):
    """Load a problem instance from a JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    m = data['m']                      # number of exams
    n = data['n']                      # number of time slots
    R = data['R']                      # proctor budget per slot
    r = data['r']                      # proctor requirements (already 1-indexed as a list)
    
    # Convert edges from 1-indexed to 0-indexed
    edges = [(i - 1, j - 1) for (i, j) in data['edges']]
    
    return m, n, R, r, edges

def build_conflict_graph(m, edges):
    """Build a NetworkX graph from the conflict edge list."""
    G = nx.Graph()
    G.add_nodes_from(range(m))
    G.add_edges_from(edges)
    return G

def get_maximal_cliques(G):
    """Return all maximal cliques in the conflict graph."""
    return list(nx.find_cliques(G))

def enumerate_feasible_groupings(m, r, R, edges):
    """
    Enumerate all feasible groupings (stable sets with proctor budget <= R).
    Uses recursive backtracking with pruning.
    """
    # Build adjacency sets for fast conflict lookup
    conflicts = {i: set() for i in range(m)}
    for (i, j) in edges:
        conflicts[i].add(j)
        conflicts[j].add(i)

    feasible_groupings = []

    def backtrack(current_group, candidates, current_load):
        # Record current group as feasible (if non-empty)
        if current_group:
            feasible_groupings.append(frozenset(current_group))

        # Try adding each candidate exam to the group
        for idx, exam in enumerate(candidates):
            # Check proctor budget
            if current_load + r[exam] > R:
                continue  # pruning: over budget, skip

            # New candidates: remove used exam, remove conflicts, remove over-budget
            new_candidates = [
                e for e in candidates[idx + 1:]  # only look forward to avoid duplicates
                if e not in conflicts[exam]       # no conflict with new exam
                and current_load + r[exam] + r[e] <= R  # rough budget check
            ]

            backtrack(current_group + [exam], new_candidates, current_load + r[exam])

    # Start with all exams as candidates
    all_exams = list(range(m))
    backtrack([], all_exams, 0)

    return feasible_groupings

def solve_lp_relaxation(m, n, R, r, edges, cliques=None):
    """
    Build and solve the LP relaxation directly with continuous variables.
    If cliques is provided, uses clique constraints (F1b). Otherwise uses edge constraints (F1a).
    """
    model = gp.Model("LP_Relaxation")
    model.Params.OutputFlag = 0

    # Continuous variables between 0 and 1
    x = model.addVars(m, n, lb=0.0, ub=1.0, name="x")
    y = model.addVars(n, lb=0.0, ub=1.0, name="y")

    # Objective
    model.setObjective(gp.quicksum(y[j] for j in range(n)), GRB.MINIMIZE)

    # Each exam assigned to exactly one slot
    for i in range(m):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n)) == 1)

    # Proctor budget
    for j in range(n):
        model.addConstr(gp.quicksum(r[i] * x[i, j] for i in range(m)) <= R * y[j])

    # Conflict constraints
    if cliques is not None:
        # F1b: clique constraints
        for clique in cliques:
            for j in range(n):
                model.addConstr(gp.quicksum(x[i, j] for i in clique) <= 1)
    else:
        # F1a: edge constraints
        for (i, ip) in edges:
            for j in range(n):
                model.addConstr(x[i, j] + x[ip, j] <= 1)

    model.optimize()

    return model.ObjVal if model.Status == GRB.OPTIMAL else None