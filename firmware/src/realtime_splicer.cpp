#include "realtime_splicer.h"
#include "config.h"

namespace {

struct State {
    RealtimeSplicerStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupRealtimeSplicer() {
    st = {};
    st.initialized = true;
    Serial.println(F("REALTIME_SPLICER_INIT"));
}

void updateRealtimeSplicer() {
    if (!st.initialized) return;
}

RealtimeSplicerStats getRealtimeSplicerStats() {
    return st.stats;
}

void serializeRealtimeSplicerStats() {
    RealtimeSplicerStats s = st.stats;
    Serial.print(F("REALTIME_SPLICER_STATS"));
    Serial.print(F(" totalSyncs="));
    Serial.print(s.totalSyncs);
    Serial.print(F(" missedWindows="));
    Serial.print(s.missedWindows);
    Serial.print(F(" bufferUnderruns="));
    Serial.print(s.bufferUnderruns);
    Serial.print(F(" avgLeadTimeMs="));
    Serial.print(s.avgLeadTimeMs);
    Serial.print(F(" maxLeadTimeMs="));
    Serial.print(s.maxLeadTimeMs);
    Serial.print(F(" syncAccuracy="));
    Serial.print(s.syncAccuracy, 2);
    Serial.println();
}
