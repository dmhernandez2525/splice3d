#include "multi_color.h"
#include "config.h"

namespace {

struct State {
    MultiColorStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupMultiColor() {
    st = {};
    st.initialized = true;
    Serial.println(F("MULTI_COLOR_INIT"));
}

void updateMultiColor() {
    if (!st.initialized) return;
}

MultiColorStats getMultiColorStats() {
    return st.stats;
}

void serializeMultiColorStats() {
    MultiColorStats s = st.stats;
    Serial.print(F("MULTI_COLOR_STATS"));
    Serial.print(F(" activeChannels="));
    Serial.print(s.activeChannels);
    Serial.print(F(" totalSwitches="));
    Serial.print(s.totalSwitches);
    Serial.print(F(" failedSwitches="));
    Serial.print(s.failedSwitches);
    Serial.print(F(" avgSwitchMs="));
    Serial.print(s.avgSwitchMs);
    Serial.print(F(" totalPurgeMm="));
    Serial.print(s.totalPurgeMm);
    Serial.print(F(" channelUtilization="));
    Serial.print(s.channelUtilization, 2);
    Serial.println();
}
