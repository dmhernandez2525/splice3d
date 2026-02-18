#include "slicer_bambu.h"
#include "config.h"

namespace {

struct State {
    SlicerBambuStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupSlicerBambu() {
    st = {};
    st.initialized = true;
    Serial.println(F("SLICER_BAMBU_INIT"));
}

void updateSlicerBambu() {
    if (!st.initialized) return;
}

SlicerBambuStats getSlicerBambuStats() {
    return st.stats;
}

void serializeSlicerBambuStats() {
    SlicerBambuStats s = st.stats;
    Serial.print(F("SLICER_BAMBU_STATS"));
    Serial.print(F(" parsedLines="));
    Serial.print(s.parsedLines);
    Serial.print(F(" amsUnitsDetected="));
    Serial.print(s.amsUnitsDetected ? F("Y") : F("N"));
    Serial.print(F(" filamentChanges="));
    Serial.print(s.filamentChanges);
    Serial.print(F(" flushVolumeMl="));
    Serial.print(s.flushVolumeMl);
    Serial.print(F(" platesProcessed="));
    Serial.print(s.platesProcessed);
    Serial.println();
}
