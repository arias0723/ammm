

class UnionFind(object):
    """Disjoint-set / Union-Find with path compression and union by rank."""
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.numComponents = n

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            next_x = self.parent[x]
            self.parent[x] = root
            x = next_x
        return root

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.numComponents -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def getComponents(self, n):
        components = {}
        for i in range(n):
            root = self.find(i)
            if root not in components:
                components[root] = []
            components[root].append(i)
        return components