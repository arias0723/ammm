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

#### Notes

- Only `BaseReassignment` strategy is not sufficient when the cut is one isolated node. Maybe we need both `BaseReassignment` and `BaseExchange` strategies ???
  - `01_small` improves with `BaseReassignment` localSearch, though the solution is NOT optimal due to the greedy knapsack
  - `02_small` does NOT improve with `BaseReassignment` localSearch as the solution is one isolated node
- The greedy Specialists assignment is NOT optimal. Explore if we need localSearch nested (or GRASP for both the cut and knapsack !!!)

- `03_small_infeasible_mincut.dat`
  - The Min-Cut: Isolates base 0. It cuts 3 pipes with demands 5, 5, 5 (total weight = 15). Because there are 3 pipes and only 2 specialists, this cut is infeasible.
  - A Heavier Cut: Isolates base 4. It cuts 2 pipes with demands 10, 10 (total weight = 20). Since there are 2 pipes and 2 specialists with enough capacity, this cut is feasible.