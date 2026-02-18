#include "wifi_manager.h"
#include "config.h"

namespace {

struct State {
    WifiManagerStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupWifiManager() {
    st = {};
    st.initialized = true;
    Serial.println(F("WIFI_MANAGER_INIT"));
}

void updateWifiManager() {
    if (!st.initialized) return;
}

WifiManagerStats getWifiManagerStats() {
    return st.stats;
}

void serializeWifiManagerStats() {
    WifiManagerStats s = st.stats;
    Serial.print(F("WIFI_MANAGER_STATS"));
    Serial.print(F(" currentMode="));
    Serial.print(s.currentMode);
    Serial.print(F(" connected="));
    Serial.print(s.connected ? F("Y") : F("N"));
    Serial.print(F(" ipAddress="));
    Serial.print(s.ipAddress);
    Serial.print(F(" rssi="));
    Serial.print(s.rssi);
    Serial.print(F(" uptimeMs="));
    Serial.print(s.uptimeMs);
    Serial.print(F(" reconnectCount="));
    Serial.print(s.reconnectCount);
    Serial.println();
}
