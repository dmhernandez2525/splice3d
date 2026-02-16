#include "mfg_ready.h"
#include "config.h"

namespace {

struct State {
    MfgReadyStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupMfgReady() {
    st = {};
    st.initialized = true;
    Serial.println(F("MFG_READY_INIT"));
}

void updateMfgReady() {
    if (!st.initialized) return;
}

MfgReadyStats getMfgReadyStats() {
    return st.stats;
}

void serializeMfgReadyStats() {
    MfgReadyStats s = st.stats;
    Serial.print(F("MFG_READY_STATS"));
    Serial.print(F(" totalTestRuns="));
    Serial.print(s.totalTestRuns);
    Serial.print(F(" passRate="));
    Serial.print(s.passRate, 2);
    Serial.print(F(" avgTestDurationMs="));
    Serial.print(s.avgTestDurationMs);
    Serial.print(F(" lastCertDate="));
    Serial.print(s.lastCertDate);
    Serial.print(F(" certValid="));
    Serial.print(s.certValid ? F("Y") : F("N"));
    Serial.print(F(" failureRate="));
    Serial.print(s.failureRate, 2);
    Serial.println();
}
