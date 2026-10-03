import time

import serial

from config import (
    CONTROL_PORT,
    MATRIX_PORT,
    BAUD_RATE,
    SERIAL_TIMEOUT,
)


class SerialManager:

    def __init__(self):

        self.control = None
        self.matrix = None

    def connect(self):

        print(
            f"[SERIAL] Opening control Arduino: "
            f"{CONTROL_PORT}"
        )

        self.control = serial.Serial(
            CONTROL_PORT,
            BAUD_RATE,
            timeout=SERIAL_TIMEOUT,
        )

        print(
            f"[SERIAL] Opening matrix Arduino: "
            f"{MATRIX_PORT}"
        )

        self.matrix = serial.Serial(
            MATRIX_PORT,
            BAUD_RATE,
            timeout=SERIAL_TIMEOUT,
        )

        # Arduinos may reset when the serial connection opens.
        time.sleep(2)

        # Discard startup garbage.
        self.control.reset_input_buffer()
        self.matrix.reset_input_buffer()

        print("[SERIAL] Both Arduinos connected.")

    def close(self):

        if self.control:
            self.control.close()

        if self.matrix:
            self.matrix.close()

    # --------------------------------------------------------
    # SEND
    # --------------------------------------------------------

    @staticmethod
    def _send(port, label, message):

        message = message.strip()

        print(
            f"[PYTHON -> {label}] {message}"
        )

        port.write(
            (message + "\n").encode("utf-8")
        )

        port.flush()

    def send_control(self, message):

        self._send(
            self.control,
            "CONTROL",
            message,
        )

    def send_matrix(self, message):

        self._send(
            self.matrix,
            "MATRIX",
            message,
        )

    # --------------------------------------------------------
    # RECEIVE FROM CONTROL ARDUINO
    # --------------------------------------------------------

    def read_control(self):

        if (
            self.control
            and self.control.in_waiting > 0
        ):

            line = (
                self.control
                .readline()
                .decode(
                    "utf-8",
                    errors="ignore",
                )
                .strip()
            )

            if line:

                print(
                    f"[CONTROL -> PYTHON] {line}"
                )

                return line

        return None