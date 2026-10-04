"""A single USB serial connection, with newline framing across partial reads."""

import time
from config import CONTROL_PORT, BAUD_RATE, SERIAL_TIMEOUT


class SerialManager:
    def __init__(self, port=CONTROL_PORT):
        self.port_name = port
        self.control = None
        self._buffer = bytearray()
        self._discard_line = False

    def connect(self):
        try:
            import serial
        except ImportError as error:
            raise RuntimeError("Install pyserial: python -m pip install -r requirements.txt") from error
        print(f"[SERIAL] Opening one Arduino: {self.port_name}")
        self.control = serial.Serial(
            self.port_name, BAUD_RATE, timeout=SERIAL_TIMEOUT, write_timeout=2,
        )
        time.sleep(2)  # Allow a board reset after opening USB serial.
        # Do not discard buffered button requests or the startup READY message.
        self.send_control("HELLO")

    def close(self):
        if self.control is not None:
            self.control.close()
            self.control = None

    def send_control(self, message):
        if self.control is None:
            raise RuntimeError("Arduino serial port is not connected")
        if "\n" in message or "\r" in message:
            raise ValueError("A serial message must be one line")
        print(f"[PYTHON -> ARDUINO] {message}")
        self.control.write((message + "\n").encode("ascii"))
        self.control.flush()

    def read_control(self):
        if self.control is None:
            return None
        # Preserve partial lines rather than treating a timeout as a delimiter.
        while self.control.in_waiting:
            data = self.control.read(1)
            if not data:
                break
            if data == b"\n":
                if self._discard_line:
                    self._discard_line = False
                    self._buffer.clear()
                    continue
                line = self._buffer.decode("ascii", errors="replace").strip()
                self._buffer.clear()
                if line:
                    print(f"[ARDUINO -> PYTHON] {line}")
                    return line
            elif not self._discard_line:
                if len(self._buffer) >= 255:
                    self._buffer.clear()
                    self._discard_line = True
                else:
                    self._buffer.extend(data)
        return None
