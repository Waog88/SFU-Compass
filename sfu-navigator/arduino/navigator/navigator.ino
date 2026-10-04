/*
  ONE-BOARD SFU NAVIGATOR -- Arduino UNO R4 WiFi

  LCD: RS=12, E=11, D4=5, D5=4, D6=3, D7=2.
  LCD VSS/RW/K -> GND, VDD -> 5V, VO -> GND (working contrast).
  Backlight A -> 5V through 220 ohms.

  Buttons: LEFT=6, SELECT=7, RIGHT=8; each button connects its pin to GND.
  Optional joystick: +5V, GND, VRx=A1, SW=7. VRy is unused.
  Set USE_JOYSTICK to 1, upload again, and release the stick to centre
  between moves. Click selects; hold SELECT for 1.2 seconds to reset.

  Python performs pathfinding over ONE USB serial port (115200 baud).
  This is landmark guidance, not live tracking or a verified campus map.
  The built-in matrix shows a campus schematic; the current segment blinks.
*/

#include <Arduino.h>
#include <LiquidCrystal.h>
#include <Arduino_LED_Matrix.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "campus_map.h"

#ifndef USE_JOYSTICK
#define USE_JOYSTICK 1
#endif

const bool JOYSTICK_REVERSED = false;
const int JOYSTICK_X = A1;
const int buttonPins[3] = {6, 7, 8}; // left, select, right
const unsigned long DEBOUNCE_MS = 30;
const unsigned long RESET_HOLD_MS = 1200;
const unsigned long ROUTE_TIMEOUT_MS = 15000;

LiquidCrystal lcd(12, 11, 5, 4, 3, 2);
ArduinoLEDMatrix matrix;
uint8_t frame[8][12] = {};

const int NUM_LOCATIONS = 12;
const char* const locations[NUM_LOCATIONS] = {
  "WMC", "Library", "SUB", "MBC", "AQ", "Shrum Chemistry",
  "Shrum Physics", "Shrum Biology", "South Sciences", "ASB", "TASC1", "TASC2"
};
const char* const displayNames[NUM_LOCATIONS] = {
  "WMC", "LIBRARY", "SUB", "MBC", "AQ", "SHRUM CHEM",
  "SHRUM PHYS", "SHRUM BIO", "SOUTH SCI", "ASB", "TASC 1", "TASC 2"
};

enum State { SELECT_START, SELECT_DESTINATION, WAITING_FOR_ROUTE,
             NAVIGATING, ARRIVED_STATE, ERROR_STATE };
State state = SELECT_START;
int startIndex = 0;
int destinationIndex = 1;
const int MAX_STEPS = 20;
char routeNames[MAX_STEPS][17] = {};
unsigned long routeDistances[MAX_STEPS] = {};
uint8_t routeMasks[MAX_STEPS][12] = {};
uint8_t campusMap[12] = {};
int routeStepCount = 0;
int currentStep = 0;
unsigned long totalDistance = 0;
bool loadingRoute = false;
unsigned long routeRequestedAt = 0;

bool rawButton[3] = {false, false, false};
bool stableButton[3] = {false, false, false};
bool pressedEvent[3] = {false, false, false};
bool releasedEvent[3] = {false, false, false};
unsigned long buttonChangedAt[3] = {};
unsigned long selectPressedAt = 0;
bool selectHoldConsumed = false;
bool joystickArmed = true;
char serialLine[96] = {};
size_t serialLength = 0;
bool discardSerialLine = false;
unsigned long lastMatrixUpdate = 0;

// Forward declarations also make the file valid outside Arduino preprocessing.
void renderStatus();
void showStartMenu();
void showDestinationMenu();
void showCurrentStep();
void resetDevice(bool notifyBackend);
void showError(const char* reason);

void showLCD(const char* first, const char* second) {
  const char* lines[2] = {first, second};
  for (int row = 0; row < 2; ++row) {
    lcd.setCursor(0, row);
    size_t length = strlen(lines[row]);
    for (int column = 0; column < 16; ++column) {
      lcd.write(column < (int)length ? lines[row][column] : ' ');
    }
  }
}

void renderStatus() {
  bool blinkOn = (millis() / 450) % 2 == 0;
  for (int row = 0; row < 8; ++row) {
    for (int column = 0; column < 12; ++column) {
      int bit = row * 12 + column;
      uint8_t flag = (uint8_t)(1 << (7 - bit % 8));
      frame[row][column] = (campusMap[bit / 8] & flag) ? 1 : 0;
      if (state == NAVIGATING && currentStep < routeStepCount &&
          (routeMasks[currentStep][bit / 8] & flag)) {
        frame[row][column] = blinkOn ? 1 : 0;
      }
    }
  }
  if (state == NAVIGATING) {
    // Step mask was already applied above; all other map pixels stay lit.
  } else if (state == ARRIVED_STATE) {
    // LCD says ARRIVED; the complete map stays steady.
  } else if (state == ERROR_STATE) {
    memset(frame, 0, sizeof(frame));
    for (int index = 0; index < 6; ++index) {
      frame[index + 1][index + 3] = 1;
      frame[index + 1][8 - index] = 1;
    }
  } else {
    int selected = state == SELECT_START ? startIndex : destinationIndex;
    frame[LOCATION_ROWS[selected]][LOCATION_COLUMNS[selected]] = blinkOn ? 1 : 0;
  }
  matrix.renderBitmap(frame, 8, 12);
  lastMatrixUpdate = millis();
}

void showStartMenu() {
  showLCD("SELECT START", displayNames[startIndex]);
  renderStatus();
}

void showDestinationMenu() {
  showLCD("DESTINATION", displayNames[destinationIndex]);
  renderStatus();
}

void resetDevice(bool notifyBackend) {
  state = SELECT_START;
  loadingRoute = false;
  routeStepCount = 0;
  currentStep = 0;
  totalDistance = 0;
  if (notifyBackend) Serial.println("RESET");
  showStartMenu();
}

void showError(const char* reason) {
  state = ERROR_STATE;
  loadingRoute = false;
  showLCD(reason, "SELECT TO RESET");
  renderStatus();
}

void showArrival() {
  state = ARRIVED_STATE;
  showLCD("ARRIVED!", displayNames[destinationIndex]);
  Serial.println("ARRIVED");
  renderStatus();
}

void showCurrentStep() {
  if (currentStep >= routeStepCount) {
    showArrival();
    return;
  }
  char first[24];
  char second[32];
  snprintf(first, sizeof(first), "TO %s", routeNames[currentStep]);
  snprintf(second, sizeof(second), "%d/%d ~%lum", currentStep + 1,
           routeStepCount, routeDistances[currentStep]);
  showLCD(first, second);
  renderStatus();
}

void requestRoute() {
  routeStepCount = currentStep = 0;
  totalDistance = 0;
  loadingRoute = false;
  state = WAITING_FOR_ROUTE;
  routeRequestedAt = millis();
  Serial.print("ROUTE|");
  Serial.print(locations[startIndex]);
  Serial.print('|');
  Serial.println(locations[destinationIndex]);
  showLCD("CALCULATING...", "SELECT TO CANCEL");
  renderStatus();
}

bool parseNumber(const char* text, unsigned long* result) {
  if (!text[0]) return false;
  for (const char* character = text; *character; ++character) {
    if (*character < '0' || *character > '9') return false;
  }
  if (strlen(text) > 7) return false;
  unsigned long value = strtoul(text, nullptr, 10);
  if (value > 1000000UL) return false;
  *result = value;
  return true;
}

int hexDigit(char value) {
  if (value >= '0' && value <= '9') return value - '0';
  if (value >= 'A' && value <= 'F') return value - 'A' + 10;
  if (value >= 'a' && value <= 'f') return value - 'a' + 10;
  return -1;
}

bool parseMask(const char* text, uint8_t* output) {
  if (strlen(text) != 24) return false;
  uint8_t temporary[12];
  for (int index = 0; index < 12; ++index) {
    int high = hexDigit(text[index * 2]);
    int low = hexDigit(text[index * 2 + 1]);
    if (high < 0 || low < 0) return false;
    temporary[index] = (uint8_t)((high << 4) | low);
  }
  memcpy(output, temporary, 12);
  return true;
}

void processSerial(char* message) {
  if (strcmp(message, "HELLO") == 0) {
    Serial.println("READY");
    return;
  }
  if (strcmp(message, "RESET") == 0) {
    resetDevice(false);
    return;
  }
  // Ignore late route responses after the user has cancelled navigation.
  if (state != WAITING_FOR_ROUTE) return;
  if (strncmp(message, "ERROR", 5) == 0) {
    showError("ROUTE ERROR");
    return;
  }
  if (strcmp(message, "BEGIN") == 0) {
    routeStepCount = currentStep = 0;
    totalDistance = 0;
    loadingRoute = true;
    return;
  }
  if (!loadingRoute) return;
  if (strncmp(message, "MAP|", 4) == 0) {
    if (!parseMask(message + 4, campusMap)) showError("BAD MAP");
    return;
  }
  if (strncmp(message, "TOTAL|", 6) == 0) {
    if (!parseNumber(message + 6, &totalDistance)) showError("BAD DISTANCE");
    return;
  }
  if (strncmp(message, "STEP|", 5) == 0) {
    char* name = message + 5;
    char* separator = strchr(name, '|');
    if (!separator) { showError("BAD STEP"); return; }
    *separator = '\0';
    char* maskSeparator = strchr(separator + 1, '|');
    if (!maskSeparator) { showError("UPDATE BACKEND"); return; }
    *maskSeparator = '\0';
    size_t length = strlen(name);
    unsigned long distance;
    if (!length || length > 16 || routeStepCount >= MAX_STEPS ||
        !parseNumber(separator + 1, &distance)) {
      showError("INVALID STEP");
      return;
    }
    uint8_t mask[12];
    if (!parseMask(maskSeparator + 1, mask)) { showError("BAD STEP MAP"); return; }
    bool hasPixel = false;
    for (int index = 0; index < 12; ++index) {
      if (mask[index] & (uint8_t)~campusMap[index]) { showError("STEP OFF MAP"); return; }
      if (mask[index]) hasPixel = true;
    }
    if (!hasPixel) { showError("EMPTY STEP MAP"); return; }
    memcpy(routeMasks[routeStepCount], mask, 12);
    strcpy(routeNames[routeStepCount], name);
    routeDistances[routeStepCount++] = distance;
    return;
  }
  if (strcmp(message, "END") == 0) {
    loadingRoute = false;
    if (!routeStepCount) { showError("NO ROUTE"); return; }
    state = NAVIGATING;
    currentStep = 0;
    showCurrentStep();
  }
}

void pollSerial() {
  // Work is bounded, so button input and matrix animation remain responsive.
  int budget = 128;
  while (budget-- > 0 && Serial.available()) {
    char character = (char)Serial.read();
    if (character == '\r') continue;
    if (character == '\n') {
      if (!discardSerialLine && serialLength) {
        serialLine[serialLength] = '\0';
        processSerial(serialLine);
      } else if (discardSerialLine && state == WAITING_FOR_ROUTE) {
        showError("MESSAGE TOO LONG");
        Serial.println("DEVICE_ERROR|MESSAGE TOO LONG");
      }
      serialLength = 0;
      discardSerialLine = false;
    } else if (!discardSerialLine) {
      if (serialLength < sizeof(serialLine) - 1) serialLine[serialLength++] = character;
      else discardSerialLine = true;
    }
  }
}

void pollButtons() {
  unsigned long now = millis();
  for (int index = 0; index < 3; ++index) {
    pressedEvent[index] = releasedEvent[index] = false;
    bool down = digitalRead(buttonPins[index]) == LOW;
    if (down != rawButton[index]) {
      rawButton[index] = down;
      buttonChangedAt[index] = now;
    }
    if (down != stableButton[index] && now - buttonChangedAt[index] >= DEBOUNCE_MS) {
      stableButton[index] = down;
      pressedEvent[index] = down;
      releasedEvent[index] = !down;
    }
  }
}

int readHorizontalAction() {
#if USE_JOYSTICK
  int reading = analogRead(JOYSTICK_X);
  if (reading > 350 && reading < 675) joystickArmed = true;
  if (!joystickArmed) return 0;
  int direction = reading < 200 ? -1 : (reading > 825 ? 1 : 0);
  if (direction) joystickArmed = false;
  return JOYSTICK_REVERSED ? -direction : direction;
#else
  if (pressedEvent[0]) return -1;
  if (pressedEvent[2]) return 1;
  return 0;
#endif
}

void handleHorizontal(int direction) {
  if (!direction) return;
  if (state == SELECT_START) {
    startIndex = (startIndex + direction + NUM_LOCATIONS) % NUM_LOCATIONS;
    showStartMenu();
  } else if (state == SELECT_DESTINATION) {
    destinationIndex = (destinationIndex + direction + NUM_LOCATIONS) % NUM_LOCATIONS;
    showDestinationMenu();
  } else if (state == NAVIGATING) {
    if (direction > 0) {
      ++currentStep;
      Serial.println("NEXT");
      showCurrentStep();
    } else if (currentStep > 0) {
      --currentStep;
      Serial.println("PREVIOUS");
      showCurrentStep();
    }
  }
}

void handleSelect() {
  if (state == SELECT_START) {
    state = SELECT_DESTINATION;
    showDestinationMenu();
  } else if (state == SELECT_DESTINATION) {
    if (startIndex == destinationIndex) {
      showLCD("SAME LOCATION", "CHANGE WITH L/R");
    } else requestRoute();
  } else if (state == NAVIGATING) {
    Serial.println("REPEAT");
    showCurrentStep();
  } else resetDevice(true); // Waiting: cancel. Arrived/error: new route.
}

void setup() {
  Serial.begin(115200);
  for (int index = 0; index < 3; ++index) pinMode(buttonPins[index], INPUT_PULLUP);
  analogReadResolution(10);
  lcd.begin(16, 2);
  matrix.begin();
  memcpy(campusMap, DEFAULT_MAP, sizeof(campusMap));
  showStartMenu();
  Serial.println("BOOT");
  Serial.println("READY");
}

void loop() {
  pollSerial();
  pollButtons();
  handleHorizontal(readHorizontalAction());
  unsigned long now = millis();
  if (pressedEvent[1]) {
    selectPressedAt = now;
    selectHoldConsumed = false;
  }
  if (stableButton[1] && !selectHoldConsumed && now - selectPressedAt >= RESET_HOLD_MS) {
    selectHoldConsumed = true;
    resetDevice(true);
  }
  // Select activates on release, so holding it cannot confirm multiple menus.
  if (releasedEvent[1] && !selectHoldConsumed) handleSelect();
  if (state == WAITING_FOR_ROUTE && now - routeRequestedAt >= ROUTE_TIMEOUT_MS) {
    showError("BACKEND TIMEOUT");
    Serial.println("DEVICE_ERROR|BACKEND TIMEOUT");
  }
  if (now - lastMatrixUpdate >= 150) renderStatus();
}
