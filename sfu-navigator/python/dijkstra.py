import heapq


def shortest_path(graph, start, destination):
    """
    Run Dijkstra's shortest-path algorithm.

    Returns:
        path: list of nodes
        distance: total path distance
    """

    if start not in graph:
        raise ValueError(f"Unknown start node: {start}")

    if destination not in graph:
        raise ValueError(
            f"Unknown destination node: {destination}"
        )

    distances = {
        node: float("inf")
        for node in graph
    }

    previous = {
        node: None
        for node in graph
    }

    distances[start] = 0

    # Entries:
    # (distance_from_start, node)

    queue = [(0, start)]

    while queue:

        current_distance, current_node = (
            heapq.heappop(queue)
        )

        # Ignore stale queue entries.
        if current_distance > distances[current_node]:
            continue

        # Because Dijkstra pops nodes in increasing distance,
        # the destination is finalized here.
        if current_node == destination:
            break

        for neighbor, edge_distance in (
            graph[current_node].items()
        ):

            candidate_distance = (
                current_distance + edge_distance
            )

            if candidate_distance < distances[neighbor]:

                distances[neighbor] = (
                    candidate_distance
                )

                previous[neighbor] = current_node

                heapq.heappush(
                    queue,
                    (
                        candidate_distance,
                        neighbor,
                    ),
                )

    if distances[destination] == float("inf"):
        return None, float("inf")

    # Reconstruct route backwards.

    path = []

    node = destination

    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()

    return path, distances[destination]