import argparse
import time

from config import LANDMARKS
from graph import GRAPH
from dijkstra import shortest_path
from route_builder import build_route
from serial_manager import SerialManager


def calculate_route(start, destination):

    if start not in LANDMARKS:
        raise ValueError(
            f"Invalid start landmark: {start}"
        )

    if destination not in LANDMARKS:
        raise ValueError(
            f"Invalid destination landmark: {destination}"
        )

    path, distance = shortest_path(
        GRAPH,
        start,
        destination,
    )

    if path is None:
        return None

    return build_route(
        GRAPH,
        path,
        distance,
    )


# ============================================================
# MOCK MODE
# ============================================================

def mock_mode():

    print()
    print("SFU NAVIGATOR -- MOCK MODE")
    print("=" * 40)

    print("\nAvailable locations:\n")

    for location in sorted(LANDMARKS):
        print(" ", location)

    print()

    start = input(
        "Start: "
    ).strip()

    destination = input(
        "Destination: "
    ).strip()

    try:

        route = calculate_route(
            start,
            destination,
        )

    except ValueError as error:

        print("\nERROR:", error)
        return

    if route is None:

        print("\nNo route found.")
        return

    print("\nRunning Dijkstra...\n")

    print("Internal route:")

    print(
        " -> ".join(
            route["full_path"]
        )
    )

    print("\nUser route:")

    print(
        " -> ".join(
            route["visible_path"]
        )
    )

    print(
        f"\nTotal distance: "
        f"{route['total_distance']} m"
    )

    print("\nInstructions:\n")

    for number, step in enumerate(
        route["steps"],
        start=1,
    ):

        print(
            f"{number}. "
            f"{step['from']} -> "
            f"{step['to']} "
            f"({step['distance']} m)"
        )


# ============================================================
# SEND ROUTE TO CONTROL ARDUINO
# ============================================================

def send_route_to_control(
    serial_manager,
    route,
):

    serial_manager.send_control("BEGIN")

    serial_manager.send_control(
        f"TOTAL|{route['total_distance']}"
    )

    for step in route["steps"]:

        serial_manager.send_control(
            "STEP|"
            f"{step['display_name']}|"
            f"{step['distance']}"
        )

    serial_manager.send_control("END")


# ============================================================
# SEND ROUTE TO MATRIX ARDUINO
# ============================================================

def send_route_to_matrix(
    serial_manager,
    route,
):

    serial_manager.send_matrix("CLEAR")

    # The matrix Arduino doesn't need hidden routing nodes.
    #
    # Example:
    #
    # ROUTE|WMC|Library|AQ|TASC1

    message = (
        "ROUTE|"
        + "|".join(
            route["visible_path"]
        )
    )

    serial_manager.send_matrix(message)

    serial_manager.send_matrix(
        "SEGMENT|0"
    )


# ============================================================
# HARDWARE MODE
# ============================================================

def hardware_mode():

    serial_manager = SerialManager()

    try:

        serial_manager.connect()

        print()
        print("SFU Navigator ready.")
        print("Waiting for Arduino input...")
        print()

        current_route = None
        current_segment = 0

        while True:

            message = (
                serial_manager.read_control()
            )

            if message is None:

                time.sleep(0.01)
                continue

            # ------------------------------------------------
            # ROUTE|WMC|TASC1
            # ------------------------------------------------

            if message.startswith("ROUTE|"):

                parts = message.split("|")

                if len(parts) != 3:

                    serial_manager.send_control(
                        "ERROR|BAD REQUEST"
                    )

                    continue

                start = parts[1]
                destination = parts[2]

                print(
                    f"\n[ROUTE] "
                    f"{start} -> {destination}"
                )

                try:

                    current_route = (
                        calculate_route(
                            start,
                            destination,
                        )
                    )

                except ValueError as error:

                    print("[ERROR]", error)

                    serial_manager.send_control(
                        "ERROR|INVALID LOCATION"
                    )

                    continue

                if current_route is None:

                    serial_manager.send_control(
                        "ERROR|NO ROUTE"
                    )

                    continue

                print(
                    "[PATH]",
                    " -> ".join(
                        current_route[
                            "full_path"
                        ]
                    ),
                )

                print(
                    "[DISTANCE]",
                    current_route[
                        "total_distance"
                    ],
                    "m",
                )

                send_route_to_control(
                    serial_manager,
                    current_route,
                )

                send_route_to_matrix(
                    serial_manager,
                    current_route,
                )

                current_segment = 0

            # ------------------------------------------------
            # NEXT
            # ------------------------------------------------

            elif message == "NEXT":

                if current_route is None:
                    continue

                maximum_segment = max(
                    0,
                    len(
                        current_route[
                            "steps"
                        ]
                    ) - 1,
                )

                current_segment = min(
                    current_segment + 1,
                    maximum_segment,
                )

                serial_manager.send_matrix(
                    f"SEGMENT|"
                    f"{current_segment}"
                )

            # ------------------------------------------------
            # PREVIOUS
            # ------------------------------------------------

            elif message == "PREVIOUS":

                if current_route is None:
                    continue

                current_segment = max(
                    current_segment - 1,
                    0,
                )

                serial_manager.send_matrix(
                    f"SEGMENT|"
                    f"{current_segment}"
                )

            # ------------------------------------------------
            # ARRIVED
            # ------------------------------------------------

            elif message == "ARRIVED":

                serial_manager.send_matrix(
                    "ARRIVED"
                )

            # ------------------------------------------------
            # RESET
            # ------------------------------------------------

            elif message == "RESET":

                current_route = None
                current_segment = 0

                serial_manager.send_matrix(
                    "CLEAR"
                )

    except KeyboardInterrupt:

        print("\nStopping SFU Navigator.")

    finally:

        serial_manager.close()


# ============================================================
# ENTRY POINT
# ============================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mock",
        action="store_true",
        help=(
            "Run pathfinding without "
            "connecting to Arduinos."
        ),
    )

    args = parser.parse_args()

    if args.mock:
        mock_mode()

    else:
        hardware_mode()


if __name__ == "__main__":
    main()