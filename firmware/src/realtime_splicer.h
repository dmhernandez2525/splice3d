/**
 * Splice3D Real-Time Printer Synchronization For Live Splicing (F10.1).
 *
 * Real-time printer position tracking, splice-ahead buffer management, timing window coordination.
 */

#ifndef REALTIME_SPLICER_H
#define REALTIME_SPLICER_H

#include <Arduino.h>

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
