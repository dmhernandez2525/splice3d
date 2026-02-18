/**
 * Splice3D Over-The-Air Firmware Update System (F9.3).
 *
 * Chunked firmware uploads with checksum verification, rollback on failure, progress reporting.
 */

#ifndef OTA_UPDATER_H
#define OTA_UPDATER_H

#include <Arduino.h>

constexpr uint16_t kMaxChunkSize = 4096;
constexpr uint32_t kMaxFirmwareSize = 1048576;
enum class OtaUpdateState : uint8_t {
    IDLE = 0,
    RECEIVING = 1,
    VERIFYING = 2,
    FLASHING = 3,
    REBOOTING = 4,
    ROLLBACK = 5,
    ERROR = 6,
};

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
