"""One-port integration checks. Run from python/: unittest discover -s tests."""

import contextlib
import io
import unittest
from config import LANDMARKS, MAX_STEPS
from graph import GRAPH
from main import calculate_route, send_route_to_control, NavigatorSession
from serial_manager import SerialManager


class Capture:
    def __init__(self):
        self.messages = []

    def send_control(self, message):
        self.messages.append(message)


class Port:
    def __init__(self):
        self.input = bytearray()
        self.output = bytearray()

    @property
    def in_waiting(self):
        return len(self.input)

    def read(self, size):
        result = bytes(self.input[:size])
        del self.input[:size]
        return result

    def write(self, data):
        self.output.extend(data)

    def flush(self):
        pass


class Integration(unittest.TestCase):
    def setUp(self):
        self.logs = contextlib.redirect_stdout(io.StringIO())
        self.logs.__enter__()

    def tearDown(self):
        self.logs.__exit__(None, None, None)

    def test_every_existing_landmark_pair(self):
        for start in LANDMARKS:
            for end in LANDMARKS:
                with self.subTest(start=start, end=end):
                    route = calculate_route(start, end)
                    self.assertIsNotNone(route)
                    self.assertEqual(route["full_path"][0], start)
                    self.assertEqual(route["full_path"][-1], end)
                    distance = sum(GRAPH[a][b] for a, b in zip(route["full_path"], route["full_path"][1:]))
                    self.assertEqual(distance, route["total_distance"])
                    self.assertEqual(sum(s["distance"] for s in route["steps"]), distance)
                    if start != end:
                        self.assertTrue(1 <= len(route["steps"]) <= MAX_STEPS)
                        self.assertEqual(route["steps"][-1]["to"], end)
                        capture = Capture()
                        send_route_to_control(capture, route)
                        self.assertEqual(capture.messages[0], "BEGIN")
                        self.assertEqual(capture.messages[-1], "END")
                        self.assertTrue(all(len(m) < 96 for m in capture.messages))

    def test_route_and_navigation_events_share_one_interface(self):
        capture = Capture()
        session = NavigatorSession(capture)
        session.handle("ROUTE|ASB|AQ")
        self.assertIsNotNone(session.route)
        if len(session.route["steps"]) > 1:
            session.handle("NEXT")
            self.assertEqual(session.current_step, 1)
            session.handle("PREVIOUS")
        self.assertEqual(session.current_step, 0)
        session.handle("REPEAT")
        session.handle("ARRIVED")
        self.assertEqual(session.current_step, len(session.route["steps"]))
        session.handle("RESET")
        self.assertIsNone(session.route)

    def test_invalid_request_clears_previous_route(self):
        capture = Capture()
        session = NavigatorSession(capture)
        session.handle("ROUTE|ASB|AQ")
        session.handle("ROUTE|RCB|AQ")
        self.assertIsNone(session.route)
        self.assertEqual(capture.messages[-1], "ERROR|INVALID ROUTE")
        session.handle("ROUTE|ASB")
        self.assertEqual(capture.messages[-1], "ERROR|BAD REQUEST")
        session.handle("ROUTE|AQ|AQ")
        self.assertEqual(capture.messages[-1], "ERROR|INVALID ROUTE")

    def test_partial_reads_and_multiple_lines(self):
        manager = SerialManager()
        manager.control = Port()
        manager.control.input.extend(b"ROUTE|AS")
        self.assertIsNone(manager.read_control())
        manager.control.input.extend(b"B|AQ\r\nNEXT\n")
        self.assertEqual(manager.read_control(), "ROUTE|ASB|AQ")
        self.assertEqual(manager.read_control(), "NEXT")

    def test_oversized_line_recovers_at_newline(self):
        manager = SerialManager()
        manager.control = Port()
        manager.control.input.extend(b"X" * 260 + b"\nRESET\n")
        self.assertEqual(manager.read_control(), "RESET")

    def test_actual_serial_output_framing(self):
        manager = SerialManager()
        manager.control = Port()
        route = calculate_route("ASB", "AQ")
        send_route_to_control(manager, route)
        lines = manager.control.output.decode("ascii").splitlines()
        self.assertEqual(lines[0], "BEGIN")
        self.assertEqual(lines[-1], "END")
        self.assertEqual(sum(line.startswith("STEP|") for line in lines), len(route["steps"]))

    def test_ready_is_not_a_reset_but_boot_is(self):
        session = NavigatorSession(Capture())
        session.handle("ROUTE|ASB|AQ")
        session.handle("READY")
        self.assertIsNotNone(session.route)
        session.handle("BOOT")
        self.assertIsNone(session.route)


if __name__ == "__main__":
    unittest.main()
