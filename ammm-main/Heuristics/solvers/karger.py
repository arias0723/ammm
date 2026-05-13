"""
AMMM Project Heuristics
Karger's algorithm for finding a randomized cut of an undirected weighted graph.

Given the pipe demands, probabilistically computes a cut by contracting
edges. Repeating this process can find non-strict min-cuts that may
result in feasible solutions when the strict min-cut cannot.
"""

import random
import math

def Karger(nBases, pipes, iterations=None):
    """
    Karger's randomized min-cut algorithm for weighted graphs.

    Args:
        nBases: number of nodes (bases)
        pipes: list of Pipe objects with getBaseI(), getBaseJ(), getDemand()
        iterations: Number of times to run the contraction. If None, defaults
                    to a heuristic amount based on the number of nodes.

    Returns:
        (cut_weight, partition): cut_weight is the total demand of the cut,
        partition is a list of length nBases with values 0 or 1.
    """

    # print('Running Karger MinCut ...')

    if iterations is None:
        # Standard heuristic for decent probability of finding minimum cuts
        iterations = max(10, int((nBases ** 2) * math.log(nBases + 1) / 2))

    orig_edges = [(p.getBaseI(), p.getBaseJ(), p.getDemand()) for p in pipes]
    
    best_cut = float('inf')
    best_partition = None

    for _ in range(iterations):
        cut_weight, partition = _karger_single_run(nBases, orig_edges)
        if cut_weight < best_cut:
            best_cut = cut_weight
            best_partition = partition

    return best_cut, best_partition

def _karger_single_run(nBases, orig_edges):
    parent = {i: i for i in range(nBases)}

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i = find(i)
        root_j = find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    nodes_count = nBases
    current_edges = [(u, v, w) for u, v, w in orig_edges]

    while nodes_count > 2:
        if not current_edges:
            break
            
        # Weighted random choice of edge to contract
        weights = [e[2] for e in current_edges]
        chosen_edge = random.choices(current_edges, weights=weights, k=1)[0]
        root_u = find(chosen_edge[0])
        root_v = find(chosen_edge[1])

        if root_u != root_v:
            union(root_u, root_v)
            nodes_count -= 1

        # Remove self-loops and merge multi-edges
        edge_map = {}
        for u, v, w in current_edges:
            ru = find(u)
            rv = find(v)
            if ru != rv:
                # canonical ordering to handle multi-edges
                if ru > rv:
                    ru, rv = rv, ru
                if (ru, rv) in edge_map:
                    edge_map[(ru, rv)] += w
                else:
                    edge_map[(ru, rv)] = w

        current_edges = [(u, v, w) for (u, v), w in edge_map.items()]

    cut_weight = sum(w for _, _, w in current_edges)

    partition = [0] * nBases
    target_cluster = find(0)
    for i in range(nBases):
        if find(i) == target_cluster:
            partition[i] = 1

    return cut_weight, partition