**Course:** ORIE 5135, Spring 2026  
**Instructor:** Andrea Lodi

---

## Problem Overview

A university must schedule m exams into time slots, minimizing the total
number of slots used, subject to:
- A proctor budget R per slot
- No two conflicting exams (sharing a student) in the same slot

The conflict structure is encoded in a graph G = (V, E).

---

## Requirements

- Python 3.8+
- [Gurobi](https://www.gurobi.com/) with a valid license (academic license works)
- gurobipy
- networkx

Install dependencies:
```bash
pip install gurobipy networkx
```

---

## How to Run

### Run a single formulation on one instance:
```bash
cd src
python formulation_f1a.py ../dataset1/instance_01.json
python formulation_f1b.py ../dataset1/instance_01.json
python formulation_f2.py  ../dataset1/instance_01.json
```

### Run the full experiment (all instances, all formulations):
```bash
cd src
python run_experiments.py
```

Results will be saved to `results/dataset1_results.csv` and
`results/dataset2_results.csv`.

> **Note:** The full experiment takes several hours due to the 600s
> time limit on Dataset 2 instances.

---

## Formulations

| Name | Description |
|------|-------------|
| F1a  | Natural ILP with pairwise edge conflict constraints |
| F1b  | Clique-strengthened ILP using maximal clique inequalities |
| F2   | Extended formulation over all feasible exam groupings (set partitioning) |

---

## Results Summary

### Dataset 1 (120s limit)
- F2 solves all 10 instances optimally in under 8 seconds
- F1a solves 5/10 optimally
- F1b solves 1/10 optimally despite identical LP bounds to F1a

### Dataset 2 (600s limit)
- F1a solves 4/9 optimally
- F1b solves 0/9 — clique constraints slow per-node solves significantly
- F2 not applicable due to exponential number of feasible groupings

---

## Note on AI Usage

Claude (Anthropic) was used to assist with code structure, LaTeX
typesetting, and debugging. All implementations were written and
verified by the student. Mathematical formulations and results were
understood and validated independently.
