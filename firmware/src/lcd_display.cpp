/**
 * LCD Display Implementation for Splice3D
 * 
 * Uses LiquidCrystal library for HD44780 compatible displays.
 */

#include "lcd_display.h"
#include "config.h"

#ifdef LCD_ENABLED

#include <LiquidCrystal.h>

// LCD dimensions (20x4 for stock Ender 3)
#define LCD_COLS 20
#define LCD_ROWS 4

// Initialize LCD with pin mapping from config.h
LiquidCrystal lcd(LCD_RS_PIN, LCD_EN_PIN, LCD_D4_PIN, LCD_D5_PIN, LCD_D6_PIN, LCD_D7_PIN);

// Custom characters for progress bar
byte progressEmpty[8] = {
    0b11111, 0b00000, 0b00000, 0b00000,
    0b00000, 0b00000, 0b00000, 0b11111
};

byte progressFull[8] = {
    0b11111, 0b11111, 0b11111, 0b11111,
    0b11111, 0b11111, 0b11111, 0b11111
};

byte progressLeft[8] = {
    0b11111, 0b10000, 0b10000, 0b10000,
    0b10000, 0b10000, 0b10000, 0b11111
};

byte progressRight[8] = {
    0b11111, 0b00001, 0b00001, 0b00001,
    0b00001, 0b00001, 0b00001, 0b11111
};

void initLCD() {
    lcd.begin(LCD_COLS, LCD_ROWS);
    lcdCreateCustomChars();
    lcdShowSplash();
}

void lcdClear() {
    lcd.clear();
}

void lcdSetCursor(uint8_t col, uint8_t row) {
    lcd.setCursor(col, row);
}

void lcdPrint(const char* text) {
    lcd.print(text);
}

void lcdPrintNumber(int value) {
    lcd.print(value);
}

void lcdPrintFloat(float value, uint8_t decimals) {
    lcd.print(value, decimals);
}

void lcdCreateCustomChars() {
    lcd.createChar(0, progressEmpty);
    lcd.createChar(1, progressFull);
    lcd.createChar(2, progressLeft);
    lcd.createChar(3, progressRight);
}

void lcdShowSplash() {
    lcdClear();
    lcdSetCursor(3, 0);
    lcdPrint("SPLICE3D v0.1.0");
    lcdSetCursor(2, 1);
    lcdPrint("Filament Splicer");
    lcdSetCursor(4, 3);
    lcdPrint("Initializing...");
    delay(1500);
}

void lcdShowStatus(const char* state, uint16_t segment, uint16_t total, float temp) {
    lcdClear();
    
    // Row 0: State
    lcdSetCursor(0, 0);
    lcdPrint("State: ");
    lcdPrint(state);
    
    // Row 1: Segment progress
    lcdSetCursor(0, 1);
    lcdPrint("Segment: ");
    lcdPrintNumber(segment);
    lcdPrint("/");
    lcdPrintNumber(total);
    
    // Row 2: Progress bar
    if (total > 0) {
        uint8_t percent = (segment * 100) / total;
        lcdShowProgress(2, percent);
    }
    
    // Row 3: Temperature
    lcdSetCursor(0, 3);
    lcdPrint("Temp: ");
    lcdPrintFloat(temp, 1);
    lcdPrint("C");
}

void lcdShowProgress(uint8_t row, uint8_t percent) {
    lcdSetCursor(0, row);
    
    // Calculate filled blocks (use 16 characters for progress)
    int filled = (percent * 16) / 100;
    
    // Draw left border
    lcd.write((uint8_t)2);
    
    // Draw progress
    for (int i = 0; i < 16; i++) {
        if (i < filled) {
            lcd.write((uint8_t)1);  // Filled
        } else {
            lcd.write((uint8_t)0);  // Empty
        }
    }
    
    // Draw right border
    lcd.write((uint8_t)3);
    
    // Show percentage
    lcdSetCursor(18, row);
    if (percent < 10) lcdPrint(" ");
    if (percent < 100) lcdPrint(" ");
    lcdPrintNumber(percent);
    lcdPrint("%");
}

void lcdShowError(const char* line1, const char* line2) {
    lcdClear();
    lcdSetCursor(0, 0);
    lcdPrint("!!! ERROR !!!");
    lcdSetCursor(0, 1);
    lcdPrint(line1);
    lcdSetCursor(0, 2);
    lcdPrint(line2);
    lcdSetCursor(0, 3);
    lcdPrint("Press to clear...");
}

void lcdShowTemp(float current, float target) {
    lcdSetCursor(0, 3);
    lcdPrint("Temp:");
    lcdPrintFloat(current, 0);
    lcdPrint("/");
    lcdPrintFloat(target, 0);
    lcdPrint("C  ");
}

#endif // LCD_ENABLED
