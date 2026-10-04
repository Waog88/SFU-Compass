# SFU Navigator: one Arduino UNO R4 WiFi

**Windows quick start:** extract the ZIP and double-click `START_NAVIGATOR.bat`.
The window lets you choose a serial port, start/stop the backend, and view its
messages. Python 3.10+ with pip and Tcl/Tk is required for initial setup; the
launcher installs pyserial into a local virtual environment automatically.
To create a standalone executable on Windows, double-click `BUILD_EXE.bat`.
The result is `dist/SFU-Navigator.exe`. This ZIP does not contain a prebuilt EXE.
See `START_HERE.txt` for the short instructions. Joystick mode is already enabled.

This version uses one UNO R4 WiFi for the existing parallel 16x2 LCD,
three buttons (or a joystick), and the board's built-in LED matrix.
Python on your laptop calculates the route. USB carries all messages through
one serial port. No second Arduino is needed.

## Start here

1. Keep your working LCD connections from the table below.
2. Connect the joystick as shown below; joystick mode is already enabled.
3. Open `arduino/navigator/navigator.ino` in Arduino IDE. This file must remain
   inside the `navigator` folder alongside `campus_map.h`. Do not add the old sketches to that folder.
4. In Boards Manager install **Arduino UNO R4 Boards** and select
   **Arduino UNO R4 WiFi**. Install **LiquidCrystal by Arduino** through
   Library Manager if needed. The R4 board package provides Arduino_LED_Matrix.
5. Upload `navigator.ino`. The LCD should say SELECT START even without Python.
6. Close Arduino Serial Monitor and Serial Plotter so Python can use the port.
7. In a terminal, change into this project's `python` folder, then run:

   ```sh
   python -m pip install -r requirements.txt
   python -m serial.tools.list_ports
   python main.py --port /dev/ttyACM0
   ```

   Use the actual port shown by the list command. On Windows, for example:

   ```sh
   python main.py --port COM3
   ```

   On Ubuntu, use `python3` if that is your Python command. For an externally
   managed Python environment, create a virtual environment first:

   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

8. Use LEFT/RIGHT to choose START. Press and release SELECT. Choose DESTINATION
   and press and release SELECT again. Python returns a route and the device
   displays its first step. Python must stay running and USB must stay connected.

## Wiring

Disconnect USB while changing wires. All grounds must be connected together.
The Arduino sitting on the breadboard does not electrically connect its headers.

| LCD pin | Label | Connection |
| --- | --- | --- |
| 1 | VSS | Arduino GND |
| 2 | VDD | Arduino 5V |
| 3 | VO | GND, matching your working contrast setup |
| 4 | RS | Arduino D12 |
| 5 | RW | GND |
| 6 | E | Arduino D11 |
| 7-10 | D0-D3 | Leave unconnected |
| 11 | D4 | Arduino D5 |
| 12 | D5 | Arduino D4 |
| 13 | D6 | Arduino D3 |
| 14 | D7 | Arduino D2 |
| 15 | A | 5V through a 220 ohm resistor |
| 16 | K | GND |

If you later use a contrast potentiometer, connect its outer terminals to 5V
and GND and its wiper to VO; remove the direct VO-to-GND connection.

| Button | Arduino pin | Other terminal |
| --- | --- | --- |
| LEFT | D6 | GND |
| SELECT | D7 | GND |
| RIGHT | D8 | GND |

The sketch uses INPUT_PULLUP. A pressed button connects the input to ground;
no external pull-up resistor is required. On four-leg tactile switches, two
legs on the same side are commonly already connected. Use the two terminals
that connect only when pressed (confirm with a multimeter if unsure).
Do not connect a button between 5V and GND.

## Optional joystick

For a standard analog joystick module with potentiometers and a push switch:

| Joystick pin | Arduino connection |
| --- | --- |
| +5V / VCC | 5V |
| GND | GND |
| VRx | A1 |
| SW | D7 |
| VRy | Leave unconnected |

This package already sets `#define USE_JOYSTICK 1`; upload the included sketch.
Tilt left/right to move one item, return to centre before the next move,
and click/release to select. If the directions are reversed, set
`JOYSTICK_REVERSED = true`. You can leave LEFT/RIGHT buttons disconnected in
joystick mode. The joystick switch replaces SELECT; an additional SELECT
button may be connected in parallel to D7 and GND.

## Device controls

| Screen | LEFT / RIGHT | Short SELECT press and release |
| --- | --- | --- |
| Start / destination menu | Previous / next location | Confirm |
| Calculating | No action | Cancel and return to start |
| Navigation | Previous / next step | Redisplay the step and send REPEAT to Python |
| Arrived / error | No action | Return to start |

Hold SELECT for 1.2 seconds at any time to reset. A held button will not keep
advancing. Navigation is manual: press RIGHT only after reaching the displayed
landmark. Advancing beyond the last step displays ARRIVED.

The first LCD row shows `TO <landmark>`. The second shows the step count and
approximate segment distance. The 8 x 12 matrix displays a simplified diagram
of the central campus buildings and connections in your existing graph.
North is up, west is left. See `docs/matrix-map.png` for the enlarged layout.

- While choosing a location, its LED blinks.
- While navigating, the pixels for the current instruction alternate on/off
  every 450 ms; the rest of the map stays lit.
- RIGHT advances both the LCD instruction and its highlighted segment;
  LEFT restores the previous instruction and segment.
- On arrival, the map stays lit and the LCD says ARRIVED. Errors show an X.

The mask covers the actual graph path between the instruction's landmarks,
including hidden junctions. For example, ASB to AQ is one instruction in this
graph, so that whole connection blinks until you advance. This does not create
additional turn instructions. Several nearby paths share LEDs at this scale;
use the LCD landmark name to identify the destination. Blinking indicates the
selected segment, not your live position or direction of travel.

`python/matrix_map.py` defines all building/junction pixels and the drawing.
After editing coordinates, run `python python/matrix_map.py` from the project
root to regenerate `arduino/navigator/campus_map.h`, then upload again.
To add RCB/Saywell later, add their verified graph connections, location menu
entries, and pixel coordinates together. The current map uses the 12 supplied
landmarks; it does not include the residence area or Gaglardi road.

## Backend and messages

`graph.py` and `dijkstra.py` retain the supplied routing data and algorithm.
`route_builder.py` adds a pixel mask to each instruction; one Arduino handles
both displays. There is no
MATRIX_PORT or separate matrix serial connection. Both directions use ASCII
messages ending with a newline, at 115200 baud.

The Arduino sends:

```text
ROUTE|ASB|AQ
NEXT
PREVIOUS
REPEAT
ARRIVED
RESET
```

Python responds to a route request:

```text
BEGIN
MAP|000F003C02C00400FE0720C7
TOTAL|250
STEP|AQ|250|00000004004004004E070000
END
```

This is the actual ASB-to-AQ response from the prototype graph; its distances
are approximate. MAP and the final STEP field contain 24 hexadecimal characters
encoding 96 row-major pixels, most significant bit first. The device stores all
step masks, so joystick navigation changes the highlight immediately. Upload
the new firmware and use the updated backend together; an older backend cannot
supply the route masks. Error responses start with
`ERROR|`. `HELLO` returns `READY`; the device emits `BOOT` on startup.
`DEVICE_ERROR|...` reports a timeout or framing problem to Python. The device
holds at most 20 steps and times out after 15 seconds without a complete route.

## Test without the board

These commands do not require pyserial:

```sh
python main.py --mock --start ASB --destination AQ
python -m unittest discover -s tests -v
```

For a serial-only device check, temporarily stop Python and open Serial Monitor
at 115200 baud with **Newline** enabled. Choose two different locations on the
device, confirm them, and send the following lines while CALCULATING is visible
(within 15 seconds). Choose ASB to AQ and paste the five lines in the protocol
example above. The LCD should show TO AQ and `1/1 ~250m`; the corresponding
map segment should blink. Close Serial Monitor before
restarting Python.

## Limits of the supplied data

- The graph explicitly labels its connections and distances as approximate
  prototype data. Validate selected paths and their starting entrances on-site.
- RCB and Saywell are not in the supplied graph or menu. To add them, first
  record walkable connections, then update `graph.py`, `LANDMARKS` and
  `SHORT_NAMES` in `config.py`, and both Arduino location arrays and
  `NUM_LOCATIONS`. Do not invent distances or connections for the demo.
- Instructions currently identify the next landmark and distance. There are
  no verified left/right turns, accessible-route attributes, live positioning,
  web frontend, or speech playback in these files.
- Python still runs on a laptop over USB. A power bank alone supplies power but
  does not connect this firmware to the backend. Wi-Fi is a later integration.
- REPEAT is an event and a display refresh, not audio. The Python session's
  `show_step()` method is the place to connect future laptop speech output.

## Verification

The package includes software tests for desktop worker startup/stop/errors,
routes between the provided landmarks, exact segment pixels for every pair,
the one-port protocol, partial serial messages, malformed requests, navigation
progress, and resets. The firmware button/joystick, parser, timeout, and arrival
logic, blinking map pixels, and previous/next segment switching were additionally exercised using native C++ hardware stubs. These checks
do not substitute for compilation with the actual UNO R4 board package, upload,
or an on-device check with your LCD and controls.
The Windows batch launchers and executable builder have not been run on Windows,
and the Tk window has not been visually tested in this headless environment.

Official references:
- https://docs.arduino.cc/hardware/uno-r4-wifi/
- https://docs.arduino.cc/learn/electronics/lcd-displays/
- https://docs.arduino.cc/tutorials/uno-r4-wifi/led-matrix/
- https://github.com/arduino-libraries/LiquidCrystal/tree/master/examples/HelloWorld
