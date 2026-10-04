"""Run the original pathfinder through one Arduino serial connection."""

import argparse
import time
from config import LANDMARKS, CONTROL_PORT, MAX_STEPS
from graph import GRAPH
from dijkstra import shortest_path
from route_builder import build_route
from serial_manager import SerialManager
from matrix_map import BASE_MASK, unpack_pixels, BASE_PIXELS


def calculate_route(start, destination):
    if start not in LANDMARKS or destination not in LANDMARKS:
        raise ValueError("Choose a location from the available landmark list")
    path, distance = shortest_path(GRAPH, start, destination)
    return None if path is None else build_route(GRAPH, path, distance)


def send_route_to_control(serial_manager, route):
    steps = route["steps"]
    if not 1 <= len(steps) <= MAX_STEPS:
        raise ValueError("Route does not fit the device's 20-step capacity")
    for step in steps:
        name = step["display_name"]
        if not name or len(name) > 16 or any(c in name for c in "|\r\n"):
            raise ValueError("Invalid LCD step label")
        name.encode("ascii")
        pixels = unpack_pixels(step["matrix_mask"])
        if not pixels or not pixels <= BASE_PIXELS:
            raise ValueError("Invalid route segment pixels")
    serial_manager.send_control("BEGIN")
    serial_manager.send_control(f"MAP|{BASE_MASK}")
    serial_manager.send_control(f"TOTAL|{int(route['total_distance'])}")
    for step in steps:
        serial_manager.send_control(
            f"STEP|{step['display_name']}|{int(step['distance'])}|{step['matrix_mask']}"
        )
    serial_manager.send_control("END")


class NavigatorSession:
    """The Arduino owns the buttons and progress; Python owns route calculation."""

    def __init__(self, serial_manager):
        self.serial = serial_manager
        self.route = None
        self.current_step = 0

    def show_step(self):
        if self.route and self.current_step < len(self.route["steps"]):
            step = self.route["steps"][self.current_step]
            print(f"[STEP {self.current_step + 1}] Go to {step['to']}, approximately {step['distance']} m")

    def handle(self, message):
        if message == "READY":
            # HELLO also returns READY; it is not a reset event.
            print("[DEVICE] One-board navigator connected")
        elif message.startswith("ROUTE|"):
            self.route = None
            self.current_step = 0
            parts = message.split("|")
            if len(parts) != 3:
                self.serial.send_control("ERROR|BAD REQUEST")
                return
            start, destination = parts[1:]
            try:
                if start == destination:
                    raise ValueError("Start and destination are the same")
                route = calculate_route(start, destination)
                if route is None:
                    self.serial.send_control("ERROR|NO ROUTE")
                    return
                send_route_to_control(self.serial, route)
                self.route = route
                print("[PATH]", " -> ".join(route["full_path"]))
                self.show_step()
            except (ValueError, KeyError) as error:
                print("[ROUTE ERROR]", error)
                self.serial.send_control("ERROR|INVALID ROUTE")
        elif message == "NEXT" and self.route:
            self.current_step = min(self.current_step + 1, len(self.route["steps"]))
            self.show_step()
        elif message == "PREVIOUS" and self.route:
            self.current_step = max(0, self.current_step - 1)
            self.show_step()
        elif message == "REPEAT":
            self.show_step()  # Add laptop speech here if desired; no audio is included.
        elif message == "ARRIVED":
            if self.route:
                self.current_step = len(self.route["steps"])
                print("[ARRIVED]", self.route["visible_path"][-1])
        elif message in ("RESET", "BOOT") or message.startswith("DEVICE_ERROR|"):
            self.route = None
            self.current_step = 0
            print("[DEVICE]", message)


def mock_mode(start=None, destination=None):
    print("Available locations:", ", ".join(sorted(LANDMARKS)))
    start = start or input("Start: ").strip()
    destination = destination or input("Destination: ").strip()
    route = calculate_route(start, destination)
    if route is None:
        print("No route found")
        return
    print("Internal path:", " -> ".join(route["full_path"]))
    print("Landmarks:", " -> ".join(route["visible_path"]))
    print(f"Prototype distance: {route['total_distance']} m")
    for number, step in enumerate(route["steps"], 1):
        print(f"{number}. Go to {step['to']} ({step['distance']} m)")


def hardware_mode(port):
    manager = SerialManager(port)
    try:
        manager.connect()
        session = NavigatorSession(manager)
        print("Ready. Choose START and DESTINATION on the device.")
        while True:
            message = manager.read_control()
            if message is None:
                time.sleep(0.005)
            else:
                session.handle(message)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        manager.close()


def main():
    parser = argparse.ArgumentParser(description="SFU navigator: one UNO R4 WiFi")
    parser.add_argument("--mock", action="store_true", help="Pathfinding without hardware")
    parser.add_argument("--port", default=CONTROL_PORT, help="Arduino USB port, e.g. COM3 or /dev/ttyACM0")
    parser.add_argument("--start", help="Start location for --mock")
    parser.add_argument("--destination", help="Destination for --mock")
    args = parser.parse_args()
    try:
        if args.mock:
            mock_mode(args.start, args.destination)
        else:
            hardware_mode(args.port)
    except Exception as error:
        parser.exit(1, f"Error: {error}\nClose Serial Monitor and check the USB port and dependencies.\n")


if __name__ == "__main__":
    main()
