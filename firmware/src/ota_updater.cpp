#include "ota_updater.h"
#include "config.h"

namespace {

struct State {
    OtaUpdaterStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupOtaUpdater() {
    st = {};
    st.initialized = true;
    Serial.println(F("OTA_UPDATER_INIT"));
}

void updateOtaUpdater() {
    if (!st.initialized) return;
}

OtaUpdaterStats getOtaUpdaterStats() {
    return st.stats;
}

void serializeOtaUpdaterStats() {
    OtaUpdaterStats s = st.stats;
    Serial.print(F("OTA_UPDATER_STATS"));
    Serial.print(F(" totalUpdates="));
    Serial.print(s.totalUpdates);
    Serial.print(F(" successfulUpdates="));
    Serial.print(s.successfulUpdates);
    Serial.print(F(" failedUpdates="));
    Serial.print(s.failedUpdates);
    Serial.print(F(" rollbackCount="));
    Serial.print(s.rollbackCount);
    Serial.print(F(" lastUpdateMs="));
    Serial.print(s.lastUpdateMs);
    Serial.print(F(" currentVersion="));
    Serial.print(s.currentVersion);
    Serial.println();
}
