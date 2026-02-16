#include "slicer_prusa.h"
#include "config.h"

namespace {

struct State {
    SlicerPrusaStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupSlicerPrusa() {
    st = {};
    st.initialized = true;
    Serial.println(F("SLICER_PRUSA_INIT"));
}

void updateSlicerPrusa() {
    if (!st.initialized) return;
}

SlicerPrusaStats getSlicerPrusaStats() {
    return st.stats;
}

void serializeSlicerPrusaStats() {
    SlicerPrusaStats s = st.stats;
    Serial.print(F("SLICER_PRUSA_STATS"));
    Serial.print(F(" parsedLines="));
    Serial.print(s.parsedLines);
    Serial.print(F(" toolChangesFound="));
    Serial.print(s.toolChangesFound);
    Serial.print(F(" mmuDetected="));
    Serial.print(s.mmuDetected ? F("Y") : F("N"));
    Serial.print(F(" errorsEncountered="));
    Serial.print(s.errorsEncountered);
    Serial.print(F(" parseComplete="));
    Serial.print(s.parseComplete ? F("Y") : F("N"));
    Serial.println();
}
