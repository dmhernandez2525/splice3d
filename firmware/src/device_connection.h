/**
 * Splice3D Serial Device Connection Manager (F8.3).
 *
 * Auto-detect connected splicer devices, manage connection state, handle reconnection.
 */

#ifndef DEVICE_CONNECTION_H
#define DEVICE_CONNECTION_H

#include <Arduino.h>

struct DeviceConnectionStats {
    bool connectedDevices;
    uint32_t totalCommands;
    uint16_t failedCommands;
    uint32_t avgLatencyMs;
    uint32_t reconnectCount;
    uint32_t scanCount;
};

void setupDeviceConnection();
void updateDeviceConnection();
DeviceConnectionStats getDeviceConnectionStats();
void serializeDeviceConnectionStats();

#endif  // DEVICE_CONNECTION_H
