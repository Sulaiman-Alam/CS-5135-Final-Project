# src/run_experiments.py
import os
import csv
import time
from formulation_f1a import solve_f1a
from formulation_f1b import solve_f1b
from formulation_f2 import solve_f2

def run_dataset(dataset_path, output_csv, formulations, time_limit, num_instances):
    """
    Run all formulations on all instances in a dataset and save results to CSV.
    
    Args:
        dataset_path: path to the dataset folder
        output_csv: path to save results CSV
        formulations: dict of {name: solver_function}
        time_limit: time limit in seconds
        num_instances: number of instances in the dataset
    """

    fieldnames = [
        "instance",
        "formulation",
        "lp_relaxation",
        "obj_value",
        "node_count",
        "solve_time",
        "optimal",
        "num_groupings"  # only relevant for F2
    ]

    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i in range(1, num_instances + 1):
            instance_name = f"instance_{i:02d}"
            filepath = os.path.join(dataset_path, f"{instance_name}.json")

            if not os.path.exists(filepath):
                print(f"  WARNING: {filepath} not found, skipping.")
                continue

            for form_name, solver in formulations.items():
                print(f"Running {form_name} on {instance_name}...")

                try:
                    results = solver(filepath, time_limit=time_limit)
                    row = {
                        "instance": instance_name,
                        "formulation": form_name,
                        "lp_relaxation": round(results["lp_relaxation"], 4) if results["lp_relaxation"] is not None else "N/A",
                        "obj_value": round(results["obj_value"], 4) if results["obj_value"] is not None else "N/A",
                        "node_count": int(results["node_count"]),
                        "solve_time": round(results["solve_time"], 2),
                        "optimal": results["optimal"],
                        "num_groupings": results.get("num_groupings", "N/A")
                    }
                except Exception as e:
                    print(f"  ERROR on {form_name} / {instance_name}: {e}")
                    row = {
                        "instance": instance_name,
                        "formulation": form_name,
                        "lp_relaxation": "ERROR",
                        "obj_value": "ERROR",
                        "node_count": "ERROR",
                        "solve_time": "ERROR",
                        "optimal": False,
                        "num_groupings": "ERROR"
                    }

                writer.writerow(row)
                csvfile.flush()  # write immediately in case of crash
                print(f"  Done. Time: {row['solve_time']}s | Optimal: {row['optimal']} | Obj: {row['obj_value']}")

    print(f"\nResults saved to {output_csv}")


if __name__ == "__main__":

    # Dataset 1 — all three formulations, 120s limit
    print("=" * 50)
    print("DATASET 1")
    print("=" * 50)
    run_dataset(
        dataset_path="../dataset1",
        output_csv="../results/dataset1_results.csv",
        formulations={
            "F1a": solve_f1a,
            "F1b": solve_f1b,
            "F2":  solve_f2
        },
        time_limit=120,
        num_instances=10
    )

    # Dataset 2 — F1a and F1b only, 600s limit
    print("=" * 50)
    print("DATASET 2")
    print("=" * 50)
    run_dataset(
        dataset_path="../dataset2",
        output_csv="../results/dataset2_results.csv",
        formulations={
            "F1a": solve_f1a,
            "F1b": solve_f1b,
        },
        time_limit=600,
        num_instances=9
    )