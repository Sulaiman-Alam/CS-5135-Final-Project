# src/formulation_f2.py
import gurobipy as gp
from gurobipy import GRB
from utils import load_instance, enumerate_feasible_groupings

def solve_f2(filepath, time_limit=120):
    m, n, R, r, edges = load_instance(filepath)

    print(f"Enumerating feasible groupings for {filepath}...")
    groupings = enumerate_feasible_groupings(m, r, R, edges)
    print(f"Found {len(groupings)} feasible groupings.")

    model = gp.Model("F2_Extended")

    # One binary variable per feasible grouping
    lam = model.addVars(len(groupings), vtype=GRB.BINARY, name="lambda")

    # Objective: minimize number of groupings (time slots) used
    model.setObjective(gp.quicksum(lam[s] for s in range(len(groupings))), GRB.MINIMIZE)

    # Set partitioning: every exam covered exactly once
    for i in range(m):
        model.addConstr(
            gp.quicksum(lam[s] for s, group in enumerate(groupings) if i in group) == 1,
            name=f"cover_{i}"
        )

    model.Params.TimeLimit = time_limit
    model.optimize()

    # Collect results
    results = {
        "lp_relaxation": None,
        "obj_value": None,
        "node_count": model.NodeCount,
        "solve_time": model.Runtime,
        "optimal": model.Status == GRB.OPTIMAL,
        "num_groupings": len(groupings)
    }

    # LP relaxation
    relaxed = model.relax()
    relaxed.optimize()
    results["lp_relaxation"] = relaxed.ObjVal

    if model.SolCount > 0:
        results["obj_value"] = model.ObjVal

    return results

if __name__ == "__main__":
    import sys
    filepath = sys.argv[1]
    results = solve_f2(filepath)
    print(results)