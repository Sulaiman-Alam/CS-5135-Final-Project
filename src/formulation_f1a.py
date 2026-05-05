# src/formulation_f1a.py
import gurobipy as gp
from gurobipy import GRB
from utils import load_instance, build_conflict_graph, solve_lp_relaxation

def solve_f1a(filepath, time_limit=120):
    m, n, R, r, edges = load_instance(filepath)
    G = build_conflict_graph(m, edges)

    # --- LP Relaxation ---
    lp_val = solve_lp_relaxation(m, n, R, r, edges, cliques=None)

    # --- Main MIP ---
    model = gp.Model("F1a_Natural")
    model.Params.OutputFlag = 0

    x = model.addVars(m, n, vtype=GRB.BINARY, name="x")
    y = model.addVars(n, vtype=GRB.BINARY, name="y")

    model.setObjective(gp.quicksum(y[j] for j in range(n)), GRB.MINIMIZE)

    for i in range(m):
        model.addConstr(gp.quicksum(x[i, j] for j in range(n)) == 1)

    for j in range(n):
        model.addConstr(gp.quicksum(r[i] * x[i, j] for i in range(m)) <= R * y[j])

    for (i, ip) in edges:
        for j in range(n):
            model.addConstr(x[i, j] + x[ip, j] <= 1)

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
    results = solve_f1a(sys.argv[1])
    print(results)