/**
 * Splice3D Esp32 Wi-Fi Connectivity Module (F9.1).
 *
 * Wi-Fi connection management with AP/STA modes, exponential backoff, and NVS credential storage.
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>

struct WifiManagerStats {
    uint16_t currentMode;
    bool connected;
    uint16_t ipAddress;
    uint16_t rssi;
    uint32_t uptimeMs;
    uint32_t reconnectCount;
    uint16_t storedNetworks;
};

void setupWifiManager();
void updateWifiManager();
WifiManagerStats getWifiManagerStats();
void serializeWifiManagerStats();

#endif  // WIFI_MANAGER_H
