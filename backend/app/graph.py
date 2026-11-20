"""Validated prerequisite DAG with deterministic, bounded reverse traversal."""

from heapq import heappop, heappush


class Graph:
    def __init__(self, source: dict):
        ids = [c["id"] for c in source["concepts"]]
        if len(set(ids)) != len(ids) or not ids or len(ids) > 12:
            raise ValueError("Expected one to twelve unique concepts")
        self.parents = {c: set() for c in ids}
        children = {c: set() for c in ids}
        for edge in source["edges"]:
            a, b = edge["prerequisite"], edge["dependent"]
            if (
                a not in self.parents
                or b not in self.parents
                or a == b
                or a in self.parents[b]
                or edge["type"] != "prerequisite"
            ):
                raise ValueError("Invalid prerequisite edge")
            self.parents[b].add(a)
            children[a].add(b)
        remaining = {c: len(p) for c, p in self.parents.items()}
        queue = []
        for concept, count in remaining.items():
            if count == 0:
                heappush(queue, concept)
        order = []
        while queue:
            node = heappop(queue)
            order.append(node)
            for child in sorted(children[node]):
                remaining[child] -= 1
                if remaining[child] == 0:
                    heappush(queue, child)
        if len(order) != len(ids):
            raise ValueError("Prerequisite cycle")
        self.order = tuple(order)
        self.parents = {c: tuple(sorted(p)) for c, p in self.parents.items()}

    def paths(self, target: str, depth: int = 3) -> dict[str, tuple[str, ...]]:
        """Shortest ancestor→target paths, then lexicographically smallest full path."""
        if target not in self.parents or not 0 <= depth <= 3:
            raise ValueError("Invalid traversal target/depth")
        found = {target: (target,)}
        frontier = [(target,)]
        for _ in range(depth):
            following = []
            for path in frontier:
                for parent in self.parents[path[0]]:
                    candidate = (parent, *path)
                    old = found.get(parent)
                    if old is None or (len(candidate), candidate) < (len(old), old):
                        found[parent] = candidate
                        following.append(candidate)
            frontier = following
        return found
