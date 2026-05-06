# numerical-optimization

Essentially solving a Minimum Cut / Graph Disconnection problem, where you want to partition the bases into two disjoint 
sets and assign specialists to destroy the pipes (edges) connecting these sets at the minimum possible cost.


## DSA

1. Graph
2. Min-Cut graph problem (Stoer-Wagner)


## Solution

A two-phase solution is proposed:

Phase 1: Stoer-Wagner min-cut to determine the partition and cut pipes
Phase 2: Greedy resource allocation of specialists to cut pipes

---
1. Compute specialists cost-benefit ratio: Ci / Wi (lower the better). This is a 0-1 knapsack reduced to greedy (suboptimal)
2. Choose a min-cut greedy approach and pop from previous ordered list (also greedy)
