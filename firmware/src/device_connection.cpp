#include "device_connection.h"
#include "config.h"

namespace {

struct State {
    DeviceConnectionStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupDeviceConnection() {
    st = {};
    st.initialized = true;
    Serial.println(F("DEVICE_CONNECTION_INIT"));
}

void updateDeviceConnection() {
    if (!st.initialized) return;
}

DeviceConnectionStats getDeviceConnectionStats() {
    return st.stats;
}

void serializeDeviceConnectionStats() {
    DeviceConnectionStats s = st.stats;
    Serial.print(F("DEVICE_CONNECTION_STATS"));
    Serial.print(F(" connectedDevices="));
    Serial.print(s.connectedDevices ? F("Y") : F("N"));
    Serial.print(F(" totalCommands="));
    Serial.print(s.totalCommands);
    Serial.print(F(" failedCommands="));
    Serial.print(s.failedCommands);
    Serial.print(F(" avgLatencyMs="));
    Serial.print(s.avgLatencyMs);
    Serial.print(F(" reconnectCount="));
    Serial.print(s.reconnectCount);
    Serial.print(F(" scanCount="));
    Serial.print(s.scanCount);
    Serial.println();
}
