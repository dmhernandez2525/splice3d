#include "slicer_orca.h"
#include "config.h"
namespace {
struct OrcaState {
    OrcaToolChange changes[kMaxOrcaToolChanges];
    uint16_t changeCount;
    OrcaColorEntry colors[kMaxOrcaColors];
    uint8_t colorCount;
    OrcaParseState parseState;
    uint16_t parsedLines;
    uint16_t errorCount;
    uint32_t totalLayers;
    float totalLengthMm;
    bool projectLoaded;
};
OrcaState os;
bool isToolChangeLine(const char* line) {
    // OrcaSlicer uses "T0", "T1", etc. at line start.
    if (line[0] != 'T') return false;
    return (line[1] >= '0' && line[1] <= '9');
}
uint8_t parseToolNumber(const char* line) {
    if (line[0] != 'T') return 255;
    return static_cast<uint8_t>(line[1] - '0');
}
bool isLayerComment(const char* line) {
    // OrcaSlicer: "; CHANGE_LAYER" or ";LAYER_CHANGE".
    if (line[0] != ';') return false;
    const char* p = line + 1;
    while (*p == ' ') p++;
    if (p[0] == 'C' && p[1] == 'H' && p[2] == 'A') return true;
    if (p[0] == 'L' && p[1] == 'A' && p[2] == 'Y') return true;
    return false;
}
bool isColorComment(const char* line) {
    // "; filament_colour = #RRGGBB".
    if (line[0] != ';') return false;
    const char* p = line + 1;
    while (*p == ' ') p++;
    return (p[0] == 'f' && p[1] == 'i' && p[2] == 'l'
            && p[3] == 'a' && p[4] == 'm');
}
}  // namespace
void setupSlicerOrca() {
    os = {};
    os.parseState = OrcaParseState::IDLE;
    Serial.println(F("SLICER_ORCA_INIT"));
}
void updateSlicerOrca() {
    // State machine driven by parseOrcaLine calls.
}
bool parseOrcaLine(const char* line, uint16_t lineNum) {
    if (!line) return false;
    os.parsedLines++;
    if (os.parseState == OrcaParseState::IDLE) {
        os.parseState = OrcaParseState::HEADER;
    }
    if (isLayerComment(line)) {
        os.totalLayers++;
        os.parseState = OrcaParseState::BODY;
        return true;
    }
    if (isColorComment(line)) {
        return true;
    }
    if (isToolChangeLine(line)) {
        uint8_t newTool = parseToolNumber(line);
        if (newTool == 255) {
            os.errorCount++;
            return false;
        }
        uint8_t prevTool = 0;
        if (os.changeCount > 0) {
            prevTool = os.changes[os.changeCount - 1].toTool;
        }
        os.parseState = OrcaParseState::TOOL_CHANGE;
        return registerOrcaToolChange(
            lineNum, os.totalLayers, prevTool, newTool, 0.0f);
    }
    return true;
}
bool extractOrcaColor(const char* comment, uint8_t toolIdx) {
    if (!comment || toolIdx >= kMaxOrcaColors) return false;
    // Parse hex color from comment string.
    const char* hash = comment;
    while (*hash && *hash != '#') hash++;
    if (*hash != '#') return false;
    hash++;
    uint32_t hex = 0;
    for (uint8_t i = 0; i < 6; i++) {
        char c = hash[i];
        hex <<= 4;
        if (c >= '0' && c <= '9') hex |= (c - '0');
        else if (c >= 'a' && c <= 'f') hex |= (c - 'a' + 10);
        else if (c >= 'A' && c <= 'F') hex |= (c - 'A' + 10);
        else return false;
    }
    return setOrcaColor(toolIdx, hex, "");
}
bool registerOrcaToolChange(
    uint32_t line, uint32_t layer,
    uint8_t from, uint8_t to, float posMm) {
    if (os.changeCount >= kMaxOrcaToolChanges) return false;
    OrcaToolChange& tc = os.changes[os.changeCount];
    tc.lineNumber = line;
    tc.layerNumber = layer;
    tc.fromTool = from;
    tc.toTool = to;
    tc.positionMm = posMm;
    tc.valid = true;
    os.changeCount++;
    Serial.print(F("ORCA_TC line="));
    Serial.print(line);
    Serial.print(F(" T"));
    Serial.print(from);
    Serial.print(F("->T"));
    Serial.println(to);
    return true;
}
bool setOrcaColor(uint8_t toolIdx, uint32_t hex, const char* name) {
    if (toolIdx >= kMaxOrcaColors) return false;
    OrcaColorEntry& c = os.colors[toolIdx];
    c.toolIndex = toolIdx;
    c.colorHex = hex;
    c.active = true;
    if (name) {
        uint8_t i = 0;
        while (name[i] && i < 15) {
            c.name[i] = name[i];
            i++;
        }
        c.name[i] = '\0';
    }
    if (toolIdx >= os.colorCount) {
        os.colorCount = toolIdx + 1;
    }
    return true;
}
OrcaRecipe generateOrcaRecipe() {
    OrcaRecipe recipe = {};
    recipe.toolChangeCount = os.changeCount;
    recipe.colorCount = os.colorCount;
    recipe.totalLayers = os.totalLayers;
    recipe.totalLengthMm = os.totalLengthMm;
    recipe.generated = (os.changeCount > 0);
    if (recipe.generated) {
        os.parseState = OrcaParseState::COMPLETE;
        os.projectLoaded = true;
    }
    Serial.print(F("ORCA_RECIPE tc="));
    Serial.print(recipe.toolChangeCount);
    Serial.print(F(" colors="));
    Serial.print(recipe.colorCount);
    Serial.print(F(" layers="));
    Serial.println(recipe.totalLayers);
    return recipe;
}
uint16_t getOrcaToolChangeCount() { return os.changeCount; }
OrcaToolChange getOrcaToolChange(uint16_t index) {
    if (index >= os.changeCount) return {};
    return os.changes[index];
}
uint8_t getOrcaColorCount() { return os.colorCount; }
OrcaColorEntry getOrcaColor(uint8_t index) {
    if (index >= kMaxOrcaColors) return {};
    return os.colors[index];
}
void resetOrcaParser() {
    os = {};
    os.parseState = OrcaParseState::IDLE;
    Serial.println(F("ORCA_RESET"));
}
OrcaSlicerStats getOrcaStats() {
    OrcaSlicerStats stats = {};
    stats.parsedLines = os.parsedLines;
    stats.toolChangesFound = os.changeCount;
    stats.colorsExtracted = os.colorCount;
    stats.errorsEncountered = os.errorCount;
    stats.state = os.parseState;
    stats.projectLoaded = os.projectLoaded;
    return stats;
}
void serializeOrcaStats() {
    OrcaSlicerStats s = getOrcaStats();
    Serial.print(F("ORCA_STATS lines="));
    Serial.print(s.parsedLines);
    Serial.print(F(" tc="));
    Serial.print(s.toolChangesFound);
    Serial.print(F(" colors="));
    Serial.print(s.colorsExtracted);
    Serial.print(F(" errors="));
    Serial.print(s.errorsEncountered);
    Serial.print(F(" state="));
    Serial.println(static_cast<uint8_t>(s.state));
}
