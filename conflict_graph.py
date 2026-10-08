from collections import deque
from models import Request


def build_conflict_graph(requests):
    """
    Build an adjacency-list conflict graph.
    Each request is a vertex.
    An edge exists when two requests clash.
    """
    graph = {request.request_id: [] for request in requests}

    for i in range(len(requests)):
        for j in range(i + 1, len(requests)):
            if requests[i].conflicts_with(requests[j]):
                graph[requests[i].request_id].append(requests[j].request_id)
                graph[requests[j].request_id].append(requests[i].request_id)

    return graph


def bfs(graph, start):
    """Breadth First Search."""
    visited = set()
    queue = deque([start])
    order = []

    while queue:
        node = queue.popleft()

        if node in visited:
            continue

        visited.add(node)
        order.append(node)

        for neighbour in graph[node]:
            if neighbour not in visited:
                queue.append(neighbour)

    return order


def dfs(graph, start):
    """Depth First Search."""
    visited = set()
    order = []

    def visit(node):
        if node in visited:
            return

        visited.add(node)
        order.append(node)

        for neighbour in graph[node]:
            visit(neighbour)

    visit(start)
    return order


def find_components(graph):
    """Find connected groups of conflicting requests."""
    visited = set()
    components = []

    for node in graph:
        if node not in visited:
            component = []
            stack = [node]

            while stack:
                current = stack.pop()

                if current in visited:
                    continue

                visited.add(current)
                component.append(current)

                for neighbour in graph[current]:
                    if neighbour not in visited:
                        stack.append(neighbour)

            components.append(component)

    return components
