# numerical-optimization

Essentially solving a Minimum Cut / Graph Disconnection problem, where you want to partition the bases into two disjoint 
sets and assign specialists to destroy the pipes (edges) connecting these sets at the minimum possible cost.


## DSA

1. Graph
2. Min-Cut graph problem (Stoer-Wagner, Karger)


## Solution

A two-phase solution is proposed:

Phase 1: Stoer-Wagner and/or Karger min-cut to determine the partition and cut pipes
  - Karger may be better because the min-cut might not be feasible another cut could be (e.g having only 2 specs, min-cut with 3 pipes vs a worse cut with 2)
  - Or change the cost function of the pipes
Phase 2: Greedy resource allocation of specialists to cut pipes

---
1. Compute specialists cost-benefit ratio: Ci / Wi (lower the better). This is assignment problem reduced to greedy (suboptimal)
2. Choose a min-cut greedy approach and pop from previous ordered list (also greedy)


#### Greedy (on greedy) (Karger modified)
```
1. Compute Specialists cost-benefit ratio
    - Ci / Wi ordered ASC (lower the better)
    - This is a 0-1 knapsack reduced to greedy (suboptimal)
2. Contract/merge highest Pipe into one node and re-attach edges (new graph). See Karger's basic algorithm!!!
3. When only 2 components/groups left, assign Specialist greedily to destroy Pipes
```

#### Local Search
```
BaseReassignment: Pick a Base and switch its component, then recalculate the solution cost
BaseExchange: NOT YET !!!
```

#### GRASP (Karger randomized + greedy knapsack)
```
1. Same as Greedy solution but contracting a random Pipe
2. When only 2 components/groups left, assign Specialist greedily to destroy Pipes
```

## Parameter Tuning For GRASP

- We tested α from 0 to 1 in increments of 0.1
- Using datasets with 100 specs and 1000 pipes (the graphs were generated sparsed, randomized, and connected)
- Without conducting the local search
- Maximum iterations for the constructive phase is set to 100
- We are keeping the best solution of all iterations per alpha value. At the end we summarize for every dataset which alpha returned the best solution, and then we select the alpha range that works the best

#### Selected strategy

- GRASP with execTime = 10s, No LS
- 10 random instances of 100 specs and 1000 pipes (~55 min to solve in CPLEX using Macbook Pro M4 32 GB ram)
- TODO: maybe generate other test suites of different sizes
- Alpha values with 0.1 increment, doing 50 iterations per alpha
  - Select the best objective (best mean + low SD combination) as the metric per each alpha value (line chart)
    - To balance a low mean objective (since this is a minimization problem) with a low standard deviation (SD), you can use a Risk-Adjusted Cost formula, commonly known as an Upper Confidence Bound (UCB).
    - The formula penalizes high variance by adding a multiple of the standard deviation to the mean:

      **Score = mean_objective + (k * std_objective)**

- Select the median, min, max time (using tuned alpha), plot and compare (bar and boxplot charts)
- Plot in latex

#### GPT suggestions

*1. Validate with Local Search*
In GRASP, the best constructive solution doesn't always lead to the best local optimum. Sometimes, a slightly more randomized construction (which might yield a worse initial score) drops the search into a different basin of attraction that yields a better final solution after Local Search.
_Improvement: Once you narrow down your top 2 to 3 α values from this pure constructive test, run a secondary tuning pass with Local Search enabled to ensure those α values still yield the best final results._

*2. Look at the Mean and Variance, Not Just the Best*
Selecting an α purely based on the absolute best iteration can make you susceptible to outliers.
_Improvement: Look at the average (mean) solution quality and the standard deviation across those 100 iterations. An α value that consistently produces good solutions (good mean, low variance) is typically much more robust than one that performs poorly on average but gets lucky once. The CSV exporter we just set up includes these metrics precisely for this reason._

*3. Instance Diversity*
The optimal α can sometimes be highly dependent on the problem topology.
_Improvement: While using 100 specialists / 1000 pipes on sparse, randomized, connected graphs is a good anchor, it's worth running the same tuning on a small batch of instances with different characteristics (e.g., 50 specs / 500 pipes, or 200 specs / 2000 pipes, or even dense graphs). This will confirm if your chosen α is universally robust or if it only works well for that specific size._

*4. Refine the Grid (Optional)*
_Improvement: If you find that the best solutions congregate around a specific sub-range (for example, between 0.2 and 0.4), you can do a fast second pass using a finer grid (increments of 0.05, such as 0.25, 0.35) inside that tight boundary to squeeze out maximum performance._


## Notes

- Only `BaseReassignment` strategy is not sufficient when the cut is one isolated node. Maybe we need both `BaseReassignment` and `BaseExchange` strategies ???
  - `01_small` improves with `BaseReassignment` localSearch, though the solution is NOT optimal due to the greedy knapsack
  - `02_small` does NOT improve with `BaseReassignment` localSearch as the solution is one isolated node
- The greedy Specialists assignment is NOT optimal. Explore if we need localSearch nested (or GRASP for both the cut and knapsack !!!)

- `03_small_infeasible_mincut.dat`
  - The Min-Cut: Isolates base 0. It cuts 3 pipes with demands 5, 5, 5 (total weight = 15). Because there are 3 pipes and only 2 specialists, this cut is infeasible.
  - A Heavier Cut: Isolates base 4. It cuts 2 pipes with demands 10, 10 (total weight = 20). Since there are 2 pipes and 2 specialists with enough capacity, this cut is feasible.