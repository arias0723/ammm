"""
AMMM Project Heuristics
Stoer-Wagner algorithm for finding the global minimum cut of an undirected weighted graph.

Given the adjacency matrix of pipe demands, computes the minimum-weight cut
(partition into two non-empty groups minimizing total demand of crossing pipes).
"""

import copy


def StoerWagner(nBases, pipes):
    """
    Stoer-Wagner minimum cut algorithm.

    Args:
        nBases: number of nodes (bases)
        pipes: list of Pipe objects with getBaseI(), getBaseJ(), getDemand()

    Returns:
        (cut_weight, partition): cut_weight is the total demand of the min cut,
        partition is a list of length nBases with values 0 or 1.
    """
    # Build adjacency matrix
    adj = [[0] * nBases for _ in range(nBases)]
    for pipe in pipes:
        i, j = pipe.getBaseI(), pipe.getBaseJ()
        adj[i][j] = pipe.getDemand()
        adj[j][i] = pipe.getDemand()

    # Track which original nodes are merged into each super-node
    merged = [[i] for i in range(nBases)]
    active = list(range(nBases))  # list of active super-nodes

    best_cut = float('inf')
    best_partition = None

    while len(active) > 1:
        # Minimum cut phase
        cut_weight, s, t, partition = _min_cut_phase(adj, active, merged, nBases)

        if cut_weight < best_cut:
            best_cut = cut_weight
            best_partition = partition

        # Merge t into s
        for node in merged[t]:
            merged[s].append(node)
        merged[t] = []

        # Update adjacency: merge t into s
        for v in active:
            if v != s and v != t:
                adj[s][v] += adj[t][v]
                adj[v][s] += adj[v][t]
                adj[t][v] = 0
                adj[v][t] = 0
        adj[s][t] = 0
        adj[t][s] = 0

        active.remove(t)

    return best_cut, best_partition


def _min_cut_phase(adj, active, merged, nBases):
    """
    Single phase of Stoer-Wagner: maximum adjacency ordering.
    Returns (cut_of_the_phase, s, t, partition).
    """
    n = len(active)
    in_A = set()
    key = {v: 0 for v in active}  # connectivity to A

    # Start with arbitrary node
    start = active[0]
    key[start] = float('inf')

    order = []
    for _ in range(n):
        # Pick node with maximum key (most tightly connected to A)
        u = max((v for v in active if v not in in_A), key=lambda v: key[v])
        in_A.add(u)
        order.append(u)

        # Update keys
        for v in active:
            if v not in in_A:
                key[v] += adj[u][v]

    # Last two nodes added
    t = order[-1]
    s = order[-2]

    # Cut of the phase = sum of edges from t to all other nodes in active
    cut_weight = sum(adj[t][v] for v in active if v != t)

    # Partition: nodes merged into t form one side
    partition = [0] * nBases
    t_nodes = set(merged[t])
    for node in t_nodes:
        partition[node] = 1

    return cut_weight, s, t, partition
