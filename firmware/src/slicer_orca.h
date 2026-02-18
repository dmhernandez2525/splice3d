/**
 * Splice3D OrcaSlicer Plugin (F7.1).
 *
 * G-code post-processor plugin for OrcaSlicer. Parses OrcaSlicer
 * tool change patterns, extracts color metadata, and generates
 * splice recipes from project files.
 */

#ifndef SLICER_ORCA_H
#define SLICER_ORCA_H

#include <Arduino.h>

constexpr uint8_t kMaxOrcaToolChanges = 64;
constexpr uint8_t kMaxOrcaColors = 8;
constexpr uint8_t kMaxOrcaFilenameLen = 32;

enum class OrcaParseState : uint8_t {
    IDLE = 0,
    HEADER,
    BODY,
    TOOL_CHANGE,
    COMPLETE,
    PARSE_ERROR,
};

struct OrcaToolChange {
    uint32_t lineNumber;
    uint32_t layerNumber;
    uint8_t fromTool;
    uint8_t toTool;
    float positionMm;
    bool valid;
};

struct OrcaColorEntry {
    uint8_t toolIndex;
    uint32_t colorHex;
    char name[16];
    bool active;
};

struct OrcaRecipe {
    uint16_t toolChangeCount;
    uint8_t colorCount;
    uint32_t totalLayers;
    float totalLengthMm;
    bool generated;
};

struct OrcaSlicerStats {
    uint16_t parsedLines;
    uint16_t toolChangesFound;
    uint8_t colorsExtracted;
    uint16_t errorsEncountered;
    OrcaParseState state;
    bool projectLoaded;
};

void setupSlicerOrca();
void updateSlicerOrca();

// Parse a G-code line for tool change patterns.
bool parseOrcaLine(const char* line, uint16_t lineNum);

// Extract color metadata from OrcaSlicer header comment.
bool extractOrcaColor(const char* comment, uint8_t toolIdx);

// Register a tool change event.
bool registerOrcaToolChange(
    uint32_t line, uint32_t layer,
    uint8_t from, uint8_t to, float posMm);

// Set color for a tool index.
bool setOrcaColor(uint8_t toolIdx, uint32_t hex, const char* name);

// Generate splice recipe from parsed data.
OrcaRecipe generateOrcaRecipe();

// Query tool changes.
uint16_t getOrcaToolChangeCount();
OrcaToolChange getOrcaToolChange(uint16_t index);

// Query colors.
uint8_t getOrcaColorCount();
OrcaColorEntry getOrcaColor(uint8_t index);

// Reset parser state.
void resetOrcaParser();

// Statistics.
OrcaSlicerStats getOrcaStats();
void serializeOrcaStats();

#endif  // SLICER_ORCA_H
