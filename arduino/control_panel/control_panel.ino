#include <Wire.h>
#include "rgb_lcd.h"


// ============================================================
// HARDWARE
// ============================================================

rgb_lcd lcd;

const int BTN_LEFT   = 2;
const int BTN_SELECT = 3;
const int BTN_RIGHT  = 4;


// ============================================================
// LOCATIONS
//
// Protocol names MUST match Python.
// ============================================================

const int NUM_LOCATIONS = 12;

const char* locations[NUM_LOCATIONS] = {
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
  "TASC2"
};


const char* displayNames[NUM_LOCATIONS] = {
  "WMC",
  "LIBRARY",
  "SUB",
  "MBC",
  "AQ",
  "SHRUM CHEM",
  "SHRUM PHYS",
  "SHRUM BIO",
  "SOUTH SCI",
  "ASB",
  "TASC 1",
  "TASC 2"
};


// ============================================================
// STATES
// ============================================================

enum State {

  SELECT_START,

  SELECT_DESTINATION,

  WAITING_FOR_ROUTE,

  NAVIGATING,

  ARRIVED_STATE,

  ERROR_STATE
};


State state = SELECT_START;


// ============================================================
// MENU
// ============================================================

int startIndex = 0;
int destinationIndex = 1;


// ============================================================
// ROUTE STORAGE
// ============================================================

const int MAX_STEPS = 20;

String routeNames[MAX_STEPS];

int routeDistances[MAX_STEPS];

int routeStepCount = 0;

int currentStep = 0;

int totalDistance = 0;


// ============================================================
// BUTTON DEBOUNCE
// ============================================================

unsigned long lastButtonTime = 0;

const unsigned long debounceDelay = 180;


bool buttonPressed(int pin) {

  if (digitalRead(pin) == LOW) {

    if (
      millis() - lastButtonTime
      > debounceDelay
    ) {

      lastButtonTime = millis();

      return true;
    }
  }

  return false;
}


// ============================================================
// BACKLIGHT
// ============================================================

void setWhite() {
  lcd.setRGB(255, 255, 255);
}


void setBlue() {
  lcd.setRGB(0, 100, 255);
}


void setGreen() {
  lcd.setRGB(0, 255, 50);
}


void setRed() {
  lcd.setRGB(255, 0, 0);
}


// ============================================================
// LCD
// ============================================================

void showLCD(
  String first,
  String second
) {

  lcd.clear();

  lcd.setCursor(0, 0);
  lcd.print(
    first.substring(0, 16)
  );

  lcd.setCursor(0, 1);
  lcd.print(
    second.substring(0, 16)
  );
}


// ============================================================
// MENUS
// ============================================================

void showStartMenu() {

  setWhite();

  showLCD(
    "SELECT START",
    displayNames[startIndex]
  );
}


void showDestinationMenu() {

  setWhite();

  showLCD(
    "DESTINATION",
    displayNames[destinationIndex]
  );
}


// ============================================================
// ROUTE REQUEST
// ============================================================

void requestRoute() {

  routeStepCount = 0;

  currentStep = 0;

  Serial.print("ROUTE|");

  Serial.print(
    locations[startIndex]
  );

  Serial.print("|");

  Serial.println(
    locations[destinationIndex]
  );

  setBlue();

  showLCD(
    "CALCULATING...",
    "PLEASE WAIT"
  );

  state = WAITING_FOR_ROUTE;
}


// ============================================================
// SHOW NAVIGATION STEP
// ============================================================

void showCurrentStep() {

  if (
    currentStep >= routeStepCount
  ) {

    showArrival();

    return;
  }

  setBlue();

  String first =
    "NEXT: "
    + routeNames[currentStep];

  String second =
    String(
      routeDistances[currentStep]
    )
    + "m";

  showLCD(
    first,
    second
  );
}


// ============================================================
// ARRIVAL
// ============================================================

void showArrival() {

  setGreen();

  showLCD(
    "ARRIVED!",
    displayNames[destinationIndex]
  );

  Serial.println("ARRIVED");

  state = ARRIVED_STATE;
}


// ============================================================
// SERIAL INPUT
// ============================================================

void processSerial(
  String message
) {

  message.trim();


  // ----------------------------------------------------------
  // BEGIN
  // ----------------------------------------------------------

  if (message == "BEGIN") {

    routeStepCount = 0;

    currentStep = 0;

    return;
  }


  // ----------------------------------------------------------
  // TOTAL|620
  // ----------------------------------------------------------

  if (
    message.startsWith("TOTAL|")
  ) {

    int separator =
      message.indexOf('|');

    totalDistance =
      message
      .substring(separator + 1)
      .toInt();

    return;
  }


  // ----------------------------------------------------------
  // STEP|LIBRARY|145
  // ----------------------------------------------------------

  if (
    message.startsWith("STEP|")
  ) {

    int first =
      message.indexOf('|');

    int second =
      message.indexOf(
        '|',
        first + 1
      );

    if (
      first != -1
      && second != -1
      && routeStepCount < MAX_STEPS
    ) {

      routeNames[routeStepCount] =
        message.substring(
          first + 1,
          second
        );

      routeDistances[routeStepCount] =
        message
        .substring(second + 1)
        .toInt();

      routeStepCount++;
    }

    return;
  }


  // ----------------------------------------------------------
  // END
  // ----------------------------------------------------------

  if (message == "END") {

    if (routeStepCount == 0) {

      setRed();

      showLCD(
        "NO ROUTE",
        "PRESS SELECT"
      );

      state = ERROR_STATE;

      return;
    }

    currentStep = 0;

    state = NAVIGATING;

    showCurrentStep();

    return;
  }


  // ----------------------------------------------------------
  // ERROR
  // ----------------------------------------------------------

  if (
    message.startsWith("ERROR")
  ) {

    setRed();

    showLCD(
      "ROUTE ERROR",
      "PRESS SELECT"
    );

    state = ERROR_STATE;

    return;
  }
}


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(115200);

  pinMode(
    BTN_LEFT,
    INPUT_PULLUP
  );

  pinMode(
    BTN_SELECT,
    INPUT_PULLUP
  );

  pinMode(
    BTN_RIGHT,
    INPUT_PULLUP
  );

  lcd.begin(16, 2);

  showStartMenu();
}


// ============================================================
// LOOP
// ============================================================

void loop() {

  // ----------------------------------------------------------
  // SERIAL FROM PYTHON
  // ----------------------------------------------------------

  if (Serial.available()) {

    String message =
      Serial.readStringUntil('\n');

    processSerial(message);
  }


  // ----------------------------------------------------------
  // START SELECTION
  // ----------------------------------------------------------

  if (state == SELECT_START) {

    if (
      buttonPressed(BTN_RIGHT)
    ) {

      startIndex++;

      if (
        startIndex >= NUM_LOCATIONS
      ) {

        startIndex = 0;
      }

      showStartMenu();
    }


    if (
      buttonPressed(BTN_LEFT)
    ) {

      startIndex--;

      if (startIndex < 0) {

        startIndex =
          NUM_LOCATIONS - 1;
      }

      showStartMenu();
    }


    if (
      buttonPressed(BTN_SELECT)
    ) {

      state =
        SELECT_DESTINATION;

      showDestinationMenu();
    }
  }


  // ----------------------------------------------------------
  // DESTINATION SELECTION
  // ----------------------------------------------------------

  else if (
    state == SELECT_DESTINATION
  ) {

    if (
      buttonPressed(BTN_RIGHT)
    ) {

      destinationIndex++;

      if (
        destinationIndex
        >= NUM_LOCATIONS
      ) {

        destinationIndex = 0;
      }

      showDestinationMenu();
    }


    if (
      buttonPressed(BTN_LEFT)
    ) {

      destinationIndex--;

      if (
        destinationIndex < 0
      ) {

        destinationIndex =
          NUM_LOCATIONS - 1;
      }

      showDestinationMenu();
    }


    if (
      buttonPressed(BTN_SELECT)
    ) {

      if (
        startIndex
        == destinationIndex
      ) {

        setRed();

        showLCD(
          "SAME LOCATION",
          "CHOOSE ANOTHER"
        );

        delay(900);

        showDestinationMenu();
      }

      else {

        requestRoute();
      }
    }
  }


  // ----------------------------------------------------------
  // NAVIGATION
  // ----------------------------------------------------------

  else if (
    state == NAVIGATING
  ) {

    // RIGHT = next instruction

    if (
      buttonPressed(BTN_RIGHT)
    ) {

      currentStep++;

      Serial.println("NEXT");

      if (
        currentStep
        >= routeStepCount
      ) {

        showArrival();
      }

      else {

        showCurrentStep();
      }
    }


    // LEFT = previous instruction

    if (
      buttonPressed(BTN_LEFT)
    ) {

      if (currentStep > 0) {

        currentStep--;

        Serial.println(
          "PREVIOUS"
        );

        showCurrentStep();
      }
    }
  }


  // ----------------------------------------------------------
  // ARRIVED
  // ----------------------------------------------------------

  else if (
    state == ARRIVED_STATE
  ) {

    if (
      buttonPressed(BTN_SELECT)
    ) {

      Serial.println("RESET");

      state = SELECT_START;

      showStartMenu();
    }
  }


  // ----------------------------------------------------------
  // ERROR
  // ----------------------------------------------------------

  else if (
    state == ERROR_STATE
  ) {

    if (
      buttonPressed(BTN_SELECT)
    ) {

      Serial.println("RESET");

      state = SELECT_START;

      showStartMenu();
    }
  }
}