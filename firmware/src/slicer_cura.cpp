#include "slicer_cura.h"
#include "config.h"

namespace {

struct State {
    SlicerCuraStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupSlicerCura() {
    st = {};
    st.initialized = true;
    Serial.println(F("SLICER_CURA_INIT"));
}

void updateSlicerCura() {
    if (!st.initialized) return;
}

SlicerCuraStats getSlicerCuraStats() {
    return st.stats;
}

void serializeSlicerCuraStats() {
    SlicerCuraStats s = st.stats;
    Serial.print(F("SLICER_CURA_STATS"));
    Serial.print(F(" parsedLines="));
    Serial.print(s.parsedLines);
    Serial.print(F(" toolChangesFound="));
    Serial.print(s.toolChangesFound);
    Serial.print(F(" blocksIdentified="));
    Serial.print(s.blocksIdentified);
    Serial.print(F(" errorsEncountered="));
    Serial.print(s.errorsEncountered);
    Serial.print(F(" pluginLoaded="));
    Serial.print(s.pluginLoaded ? F("Y") : F("N"));
    Serial.println();
}
