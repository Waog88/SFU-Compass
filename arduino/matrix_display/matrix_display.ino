#include "Arduino_LED_Matrix.h"


ArduinoLEDMatrix matrix;


// ============================================================
// MATRIX BUFFER
// ============================================================

uint8_t frame[8][12];


// ============================================================
// STATE
// ============================================================

int currentSegment = 0;

bool blinkState = true;

bool navigating = false;

unsigned long lastBlink = 0;

const unsigned long blinkInterval = 450;


// ============================================================
// CLEAR
// ============================================================

void clearFrame() {

  for (int row = 0; row < 8; row++) {

    for (int col = 0; col < 12; col++) {

      frame[row][col] = 0;
    }
  }
}


// ============================================================
// BASE SFU SCHEMATIC
//
// NOT GEOGRAPHICALLY FINAL.
//
// Think subway diagram rather than Google Maps.
//
//  WMC -- LIB -- SUB
//                 |
//                MBC
//                 |
//                 AQ
//                 |
//              SHRUM -- ASB -- TASC
//
// ============================================================

void drawBaseMap() {

  clearFrame();


  // WEST / CENTRAL CAMPUS

  for (
    int column = 0;
    column <= 5;
    column++
  ) {

    frame[2][column] = 1;
  }


  // CENTRAL SPINE

  frame[3][5] = 1;
  frame[4][5] = 1;
  frame[5][5] = 1;


  // EAST CAMPUS

  for (
    int column = 5;
    column <= 11;
    column++
  ) {

    frame[5][column] = 1;
  }


  // Small visual branches

  frame[1][2] = 1;
  frame[1][5] = 1;

  frame[6][7] = 1;
}


// ============================================================
// ROUTE SEGMENT
//
// Current prototype maps route step number onto one of the
// schematic sections.
//
// We will replace this with exact landmark -> LED paths once
// the full electronics pipeline works.
// ============================================================

void drawActiveSegment(
  int segment
) {

  if (!blinkState) {
    return;
  }


  // SEGMENT 0:
  // west campus

  if (segment == 0) {

    frame[2][0] = 1;
    frame[1][0] = 1;
    frame[3][0] = 1;

    frame[2][1] = 1;
    frame[1][1] = 1;
    frame[3][1] = 1;

    frame[2][2] = 1;
    frame[1][2] = 1;
    frame[3][2] = 1;
  }


  // SEGMENT 1:
  // west -> centre

  else if (segment == 1) {

    for (
      int column = 3;
      column <= 5;
      column++
    ) {

      frame[1][column] = 1;
      frame[2][column] = 1;
      frame[3][column] = 1;
    }
  }


  // SEGMENT 2:
  // central vertical

  else if (segment == 2) {

    for (
      int row = 2;
      row <= 5;
      row++
    ) {

      frame[row][4] = 1;
      frame[row][5] = 1;
      frame[row][6] = 1;
    }
  }


  // SEGMENT 3:
  // central -> east

  else if (segment == 3) {

    for (
      int column = 5;
      column <= 8;
      column++
    ) {

      frame[4][column] = 1;
      frame[5][column] = 1;
      frame[6][column] = 1;
    }
  }


  // SEGMENT 4+
  // east campus

  else {

    for (
      int column = 8;
      column <= 11;
      column++
    ) {

      frame[4][column] = 1;
      frame[5][column] = 1;
      frame[6][column] = 1;
    }
  }
}


// ============================================================
// RENDER NAVIGATION
// ============================================================

void renderNavigation() {

  drawBaseMap();

  drawActiveSegment(
    currentSegment
  );

  matrix.renderBitmap(
    frame,
    8,
    12
  );
}


// ============================================================
// ARRIVAL CHECKMARK
// ============================================================

void showArrival() {

  navigating = false;

  clearFrame();


  // Check mark

  frame[4][1] = 1;

  frame[5][2] = 1;

  frame[6][3] = 1;

  frame[5][4] = 1;

  frame[4][5] = 1;

  frame[3][6] = 1;

  frame[2][7] = 1;

  frame[1][8] = 1;


  matrix.renderBitmap(
    frame,
    8,
    12
  );
}


// ============================================================
// PROCESS SERIAL
// ============================================================

void processMessage(
  String message
) {

  message.trim();


  // ----------------------------------------------------------
  // CLEAR
  // ----------------------------------------------------------

  if (message == "CLEAR") {

    navigating = false;

    clearFrame();

    matrix.renderBitmap(
      frame,
      8,
      12
    );

    return;
  }


  // ----------------------------------------------------------
  // ROUTE|WMC|Library|AQ|...
  //
  // For now we don't need to parse individual names.
  // Receiving ROUTE simply tells the display that navigation
  // has begun.
  //
  // Later we'll use these names to render the exact selected
  // schematic path.
  // ----------------------------------------------------------

  if (
    message.startsWith("ROUTE|")
  ) {

    currentSegment = 0;

    navigating = true;

    blinkState = true;

    renderNavigation();

    return;
  }


  // ----------------------------------------------------------
  // SEGMENT|2
  // ----------------------------------------------------------

  if (
    message.startsWith("SEGMENT|")
  ) {

    int separator =
      message.indexOf('|');

    currentSegment =
      message
      .substring(separator + 1)
      .toInt();

    navigating = true;

    blinkState = true;

    renderNavigation();

    return;
  }


  // ----------------------------------------------------------
  // ARRIVED
  // ----------------------------------------------------------

  if (message == "ARRIVED") {

    showArrival();

    return;
  }
}


// ============================================================
// SETUP
// ============================================================

void setup() {

  Serial.begin(115200);

  matrix.begin();

  clearFrame();

  matrix.renderBitmap(
    frame,
    8,
    12
  );
}


// ============================================================
// LOOP
// ============================================================

void loop() {

  // ----------------------------------------------------------
  // SERIAL
  // ----------------------------------------------------------

  if (Serial.available()) {

    String message =
      Serial.readStringUntil('\n');

    processMessage(message);
  }


  // ----------------------------------------------------------
  // BLINK ACTIVE ROUTE
  // ----------------------------------------------------------

  if (
    navigating
    && millis() - lastBlink
       >= blinkInterval
  ) {

    lastBlink = millis();

    blinkState = !blinkState;

    renderNavigation();
  }
}
