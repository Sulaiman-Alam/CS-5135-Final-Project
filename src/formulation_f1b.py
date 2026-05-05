# src/formulation_f1b.py
import gurobipy as gp
from gurobipy import GRB
from utils import load_instance, build_conflict_graph, get_maximal_cliques, solve_lp_relaxation

def solve_f1b(filepath, time_limit=120):
    m, n, R, r, edges = load_instance(filepath)
    G = build_conflict_graph(m, edges)
    cliques = get_maximal_cliques(G)

    # --- LP Relaxation ---
    lp_val = solve_lp_relaxation(m, n, R, r, edges, cliques=cliques)

    # --- Main MIP ---
    model = gp.Model("F1b_Clique_Strengthened")
    model.Params.OutputFlag = 0

    x = model.addVars(m, n, vtype=GRB.BINARY, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    model.setObjective(gp.quicksum(y[j] for j in range(n)), GRB.MINIMIZE)

    for i in range(m):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n)) == 1)

    for j in range(n):
        model.addConstr(gp.quicksum(r[i] * x[i, j] for i in range(m)) <= R * y[j])

    for idx, clique in enumerate(cliques):
        for j in range(n):
            model.addConstr(gp.quicksum(x[i, j] for i in clique) <= 1)

    model.Params.TimeLimit = time_limit
    model.optimize()

    return {
        "lp_relaxation": lp_val,
        "obj_value": model.ObjVal if model.SolCount > 0 else None,
        "node_count": model.NodeCount,
        "solve_time": model.Runtime,
        "optimal": model.Status == GRB.OPTIMAL
    }

if __name__ == "__main__":
    import sys
    results = solve_f1b(sys.argv[1])
    print(results)