/**
 * Splice3D Real-Time Printer Synchronization For Live Splicing (F10.1).
 *
 * Real-time printer position tracking, splice-ahead buffer management, timing window coordination.
 */

#ifndef REALTIME_SPLICER_H
#define REALTIME_SPLICER_H

#include <Arduino.h>

constexpr uint8_t kSpliceBufferSize = 8;
constexpr uint8_t kMaxTimingWindows = 16;
enum class SyncState : uint8_t {
    IDLE = 0,
    SYNCING = 1,
    AHEAD = 2,
    BEHIND = 3,
    CRITICAL = 4,
    PAUSED = 5,
    ERROR = 6,
};

struct RealtimeSplicerStats {
    uint32_t totalSyncs;
    uint16_t missedWindows;
    uint16_t bufferUnderruns;
    uint32_t avgLeadTimeMs;
    uint32_t maxLeadTimeMs;
    float syncAccuracy;
};

void setupRealtimeSplicer();
void updateRealtimeSplicer();
RealtimeSplicerStats getRealtimeSplicerStats();
void serializeRealtimeSplicerStats();

#endif  // REALTIME_SPLICER_H
