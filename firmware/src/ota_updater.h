/**
 * Splice3D Over-The-Air Firmware Update System (F9.3).
 *
 * Chunked firmware uploads with checksum verification, rollback on failure, progress reporting.
 */

#ifndef OTA_UPDATER_H
#define OTA_UPDATER_H

#include <Arduino.h>

struct OtaUpdaterStats {
    uint32_t totalUpdates;
    uint16_t successfulUpdates;
    uint16_t failedUpdates;
    uint32_t rollbackCount;
    uint32_t lastUpdateMs;
    uint16_t currentVersion;
};

void setupOtaUpdater();
void updateOtaUpdater();
OtaUpdaterStats getOtaUpdaterStats();
void serializeOtaUpdaterStats();

#endif  // OTA_UPDATER_H
