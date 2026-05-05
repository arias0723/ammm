# numerical-optimization

Essentially solving a Minimum Cut / Graph Disconnection problem, where you want to partition the bases into two disjoint 
sets and assign specialists to destroy the pipes (edges) connecting these sets at the minimum possible cost.


## DSA

1. Graph
2. Min-Cut graph problem (Karger's basic algorithm)
3. UnionFind DS


## Solution

1. Compute specialists cost-benefit ratio: Ci / Wi (lower the better). This is a 0-1 knapsack reduced to greedy (suboptimal)
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



