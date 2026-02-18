/**
 * Splice3D Esp32 Wi-Fi Connectivity Module (F9.1).
 *
 * Wi-Fi connection management with AP/STA modes, exponential backoff, and NVS credential storage.
 */

#ifndef WIFI_MANAGER_H
#define WIFI_MANAGER_H

#include <Arduino.h>

constexpr uint8_t kMaxSsidLength = 32;
constexpr uint8_t kMaxPasswordLength = 64;
constexpr uint8_t kMaxStoredNetworks = 8;

enum class WifiMode : uint8_t {
    OFF = 0, STA = 1, AP = 2, STA_AP = 3,
};

enum class WifiConnectionState : uint8_t {
    IDLE = 0, SCANNING, CONNECTING, CONNECTED,
    DISCONNECTED, AP_ACTIVE, ERROR,
};

struct WifiManagerStats {
    uint16_t currentMode;
    bool connected;
    uint32_t ipAddress;
    int16_t rssi;
    uint32_t uptimeMs;
    uint32_t reconnectCount;
    uint16_t storedNetworks;
};

void setupWifiManager();
void updateWifiManager();
WifiManagerStats getWifiManagerStats();
void serializeWifiManagerStats();

#endif  // WIFI_MANAGER_H
