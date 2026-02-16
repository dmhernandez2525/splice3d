#include "gcode_preview.h"
#include "config.h"

namespace {

struct State {
    GcodePreviewStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupGcodePreview() {
    st = {};
    st.initialized = true;
    Serial.println(F("GCODE_PREVIEW_INIT"));
}

void updateGcodePreview() {
    if (!st.initialized) return;
}

GcodePreviewStats getGcodePreviewStats() {
    return st.stats;
}

void serializeGcodePreviewStats() {
    GcodePreviewStats s = st.stats;
    Serial.print(F("GCODE_PREVIEW_STATS"));
    Serial.print(F(" totalLayers="));
    Serial.print(s.totalLayers);
    Serial.print(F(" totalColorZones="));
    Serial.print(s.totalColorZones);
    Serial.print(F(" totalSplicePoints="));
    Serial.print(s.totalSplicePoints);
    Serial.print(F(" filamentUsedMm="));
    Serial.print(s.filamentUsedMm);
    Serial.print(F(" previewReady="));
    Serial.print(s.previewReady ? F("Y") : F("N"));
    Serial.println();
}
