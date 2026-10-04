from config import LANDMARKS, SHORT_NAMES
from matrix_map import mask_for_path


def visible_route(full_path):
    """
    Remove hidden routing nodes.
    """

    return [
        node
        for node in full_path
        if node in LANDMARKS
    ]


def build_steps(graph, full_path):
    """
    Convert the detailed graph path into landmark-to-landmark
    navigation steps.

    Hidden routing nodes are absorbed into the distance between
    visible landmarks.
    """

    if not full_path:
        return []

    steps = []

    current_landmark = None
    distance_since_landmark = 0
    segment_start = 0

    for index, node in enumerate(full_path):

        if index == 0:

            if node in LANDMARKS:
                current_landmark = node

            continue

        previous_node = full_path[index - 1]

        edge_distance = (
            graph[previous_node][node]
        )

        distance_since_landmark += edge_distance

        if node in LANDMARKS:

            if current_landmark is not None:

                steps.append({
                    "from": current_landmark,
                    "to": node,
                    "display_name": SHORT_NAMES[node],
                    "distance": distance_since_landmark,
                    "matrix_mask": mask_for_path(full_path[segment_start:index + 1]),
                })

            current_landmark = node
            distance_since_landmark = 0
            segment_start = index

    return steps


def build_route(graph, full_path, total_distance):
    """
    Build one route object for the rest of the program.
    """

    return {
        "full_path": full_path,
        "visible_path": visible_route(full_path),
        "total_distance": total_distance,
        "steps": build_steps(graph, full_path),
    }
