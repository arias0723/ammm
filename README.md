# AMMM

Essentially solving a Minimum Cut / Graph Disconnection problem, where you want to partition the bases into two disjoint 
sets and assign specialists to destroy the pipes (edges) connecting these sets at the minimum possible cost.

## Instructions

#### CPLEX
- Import the project into CPLEX: `File -> Import existing OPL projects -> Select root directory`.
- Select the directory named `ilp_model` from the main folder.
- To execute different instances, update the data file reference in the `main.mod` file. For example, change line 7 to point to your desired file (e.g., `"project.n.dat"`).

#### HEURISTICS AND INSTANCE GENERATOR
- Open the cloned repository in a Python IDE (e.g., **PyCharm**).
- Create run configurations for `Main.py` in the `Heuristics` folder and for `MainGen.py` in the `InstanceGenerator` folder.
- To generate new instances, modify the `config.dat` setup in the `InstanceGenerator/config` folder, then run `InstanceGenerator/MainGen.py`.
- Generated instances will be saved in the `InstanceGenerator/output` folder using the `fileNamePrefix` specified in `config.dat`.
- To execute an instance using heuristics, modify `config.dat` within the `Heuristics/config` folder, then run `Heuristics/Main.py`. Note that instances to be executed must be placed in the `Heuristics/data` folder:
  - The instance filename is specified by the `inputDataFile` property and maintains the same structure as the CPLEX instances.
  - The algorithm type and its parameters are specified under the `solver` property within the same config file, and can be tuned as desired.
  - The expected output solution path is determined by the `solutionFile` property in the config file.


## DSA

1. Graph
2. Min-Cut graph problem (Stoer-Wagner, Karger)


## Notes

- Only `BaseReassignment` strategy is not sufficient when the cut is one isolated node. Maybe we need both `BaseReassignment` and `BaseExchange` strategies ???
  - `01_small` improves with `BaseReassignment` localSearch, though the solution is NOT optimal due to the greedy knapsack
  - `02_small` does NOT improve with `BaseReassignment` localSearch as the solution is one isolated node
- The greedy Specialists assignment is NOT optimal. Explore if we need localSearch nested (or GRASP for both the cut and knapsack !!!)

- `03_small_infeasible_mincut.dat`
  - The Min-Cut: Isolates base 0. It cuts 3 pipes with demands 5, 5, 5 (total weight = 15). Because there are 3 pipes and only 2 specialists, this cut is infeasible.
  - A Heavier Cut: Isolates base 4. It cuts 2 pipes with demands 10, 10 (total weight = 20). Since there are 2 pipes and 2 specialists with enough capacity, this cut is feasible.