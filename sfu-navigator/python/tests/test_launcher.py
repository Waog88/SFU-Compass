"""Headless tests for desktop worker startup, route handling, stop, and errors."""
import queue
import threading
import unittest
from launcher import run_backend


class LauncherWorker(unittest.TestCase):
    def test_route_exchange_and_port_cleanup(self):
        events = queue.Queue()
        stop = threading.Event()

        class Manager:
            def __init__(self, port):
                self.port = port
                self.closed = False
                self.sent = []
                self.received = iter(["ROUTE|ASB|AQ", "NEXT", "ARRIVED"])

            def connect(self):
                pass

            def read_control(self):
                try:
                    return next(self.received)
                except StopIteration:
                    stop.set()
                    return None

            def send_control(self, message):
                self.sent.append(message)

            def close(self):
                self.closed = True

        manager = Manager("COM_TEST")
        run_backend("COM_TEST", stop, events, lambda port: manager)
        self.assertTrue(manager.closed)
        self.assertEqual(manager.sent[0], "BEGIN")
        self.assertEqual(manager.sent[-1], "END")
        collected = list(events.queue)
        self.assertTrue(any(kind == "status" for kind, _ in collected))
        self.assertEqual(collected[-1][0], "stopped")

    def test_connection_failure_is_visible_and_port_is_closed(self):
        events = queue.Queue()
        stop = threading.Event()

        class Failing:
            closed = False

            def connect(self):
                raise OSError("Port is busy")

            def close(self):
                self.closed = True

        manager = Failing()
        run_backend("COM_TEST", stop, events, lambda port: manager)
        self.assertTrue(manager.closed)
        self.assertIn(("error", "Port is busy"), list(events.queue))
        self.assertEqual(list(events.queue)[-1][0], "stopped")

    def test_stopping_during_connect_releases_port(self):
        events = queue.Queue()
        stop = threading.Event()

        class Manager:
            closed = False

            def connect(self):
                stop.set()

            def close(self):
                self.closed = True

        manager = Manager()
        run_backend("COM_TEST", stop, events, lambda port: manager)
        self.assertTrue(manager.closed)
        self.assertEqual(list(events.queue), [("stopped", None)])


if __name__ == "__main__":
    unittest.main()
