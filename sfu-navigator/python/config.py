# ============================================================
# SFU Navigator Configuration
# ============================================================

BAUD_RATE = 115200

# Ubuntu examples:
#   /dev/ttyACM0
#   /dev/ttyACM1
#
# Windows examples:
#   COM3
#   COM4

CONTROL_PORT = "/dev/ttyACM0"
MATRIX_PORT = "/dev/ttyACM1"

SERIAL_TIMEOUT = 0.1


LANDMARKS = {
    "WMC",
    "Library",
    "SUB",
    "MBC",
    "AQ",
    "Shrum Chemistry",
    "Shrum Physics",
    "Shrum Biology",
    "South Sciences",
    "ASB",
    "TASC1",
    "TASC2",
}


# Names sent to the 16x2 LCD.
SHORT_NAMES = {
    "WMC": "WMC",
    "Library": "LIBRARY",
    "SUB": "SUB",
    "MBC": "MBC",
    "AQ": "AQ",
    "Shrum Chemistry": "SHRUM CHEM",
    "Shrum Physics": "SHRUM PHYS",
    "Shrum Biology": "SHRUM BIO",
    "South Sciences": "SOUTH SCI",
    "ASB": "ASB",
    "TASC1": "TASC 1",
    "TASC2": "TASC 2",
}