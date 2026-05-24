# AMMM

Essentially solving a Minimum Cut / Graph Disconnection problem, where you want to partition the bases into two disjoint 
sets and assign specialists to destroy the pipes (edges) connecting these sets at the minimum possible cost.

## Instructions

#### CPLEX
- Import the project in CPLEX: File -> Import existing OPL projects -> Select root directory.
- Select the directory named Cplex from the main folder.
- For executing the instances change the **n** in the file name of the data variable in the 7th line of the `main.mod` file.

#### HEURISTICS AND INSTANCE GENERATOR
- Open the cloned folder on a Python IDE, preferably **PyCharm**
- Create the run configurations for the Main.py of the Heuristics folder and for the Main.py of the InstanceGenerator folder.
- The instances are generated modifying the config file in the config folder of the InstanceGenerator folder and executing the run configuration assigned to the InstanceGenerator.
- These new instances will be generated in the folder "output" with fileNamePrefix set in config.dat.
- To execute an instance, change the configuration on the config file in the config folder of the Heuristics folder and then run the run configuration of the main in heuristics, the instances to execute must be in the data folder:
   -> The file name of the instance is at "inputDataFile" and has the same structure as the CPLEX instances.
   -> The algorithm type and its parameters are in the same config file, in "solver", and can be tuned as desired.
   -> The solution of the heuristic algorithm is set by "solutionFile" in config file.


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