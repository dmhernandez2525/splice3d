/**
 * LCD Display Handler for Splice3D
 * 
 * Supports stock Ender 3 LCD (HD44780 compatible) connected to EXP1.
 */

#ifndef LCD_DISPLAY_H
#define LCD_DISPLAY_H

#include <Arduino.h>
#include "config.h"

#ifdef LCD_ENABLED

/**
 * Initialize the LCD display.
 */
void initLCD();

/**
 * Clear the display.
 */
void lcdClear();

/**
 * Set cursor position.
 * @param col Column (0-19)
 * @param row Row (0-3)
 */
void lcdSetCursor(uint8_t col, uint8_t row);

/**
 * Print text to LCD.
 * @param text Text to display
 */
void lcdPrint(const char* text);

/**
 * Print formatted number.
 * @param value Number to display
 */
void lcdPrintNumber(int value);

/**
 * Print float with precision.
 * @param value Float to display
 * @param decimals Decimal places
 */
void lcdPrintFloat(float value, uint8_t decimals = 1);

/**
 * Show splash screen.
 */
void lcdShowSplash();

/**
 * Show status screen.
 * @param state Current state name
 * @param segment Current segment number
 * @param total Total segments
 * @param temp Current temperature
 */
void lcdShowStatus(const char* state, uint16_t segment, uint16_t total, float temp);

/**
 * Show progress bar.
 * @param row Row to show progress on
 * @param percent Percentage (0-100)
 */
void lcdShowProgress(uint8_t row, uint8_t percent);

/**
 * Show error message.
 * @param line1 First line
 * @param line2 Second line
 */
void lcdShowError(const char* line1, const char* line2);

/**
 * Show temperature.
 * @param current Current temp
 * @param target Target temp
 */
void lcdShowTemp(float current, float target);

/**
 * Custom character definitions for progress bar.
 */
void lcdCreateCustomChars();

#endif // LCD_ENABLED

#endif // LCD_DISPLAY_H
