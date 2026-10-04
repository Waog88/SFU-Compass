"""One-board configuration. Names must match the Arduino menu exactly."""

BAUD_RATE = 115200
CONTROL_PORT = "/dev/ttyACM0"  # Windows: e.g. "COM3"; override with --port.
SERIAL_TIMEOUT = 0.05
MAX_STEPS = 20

LANDMARKS = {
    "WMC", "Library", "SUB", "MBC", "AQ", "Shrum Chemistry",
    "Shrum Physics", "Shrum Biology", "South Sciences", "ASB", "TASC1", "TASC2",
}

SHORT_NAMES = {
    "WMC": "WMC", "Library": "LIBRARY", "SUB": "SUB", "MBC": "MBC",
    "AQ": "AQ", "Shrum Chemistry": "SHRUM CHEM", "Shrum Physics": "SHRUM PHYS",
    "Shrum Biology": "SHRUM BIO", "South Sciences": "SOUTH SCI", "ASB": "ASB",
    "TASC1": "TASC 1", "TASC2": "TASC 2",
}
