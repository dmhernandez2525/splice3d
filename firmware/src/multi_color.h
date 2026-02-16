/**
 * Splice3D 8+ Color Input Channel Support (F10.2).
 *
 * Multi-channel filament management with input selection, switching coordination, per-channel stats.
 */

#ifndef MULTI_COLOR_H
#define MULTI_COLOR_H

#include <Arduino.h>

struct MultiColorStats {
    uint16_t activeChannels;
    uint32_t totalSwitches;
    uint16_t failedSwitches;
    uint32_t avgSwitchMs;
    uint32_t totalPurgeMm;
    float channelUtilization;
};

void setupMultiColor();
void updateMultiColor();
MultiColorStats getMultiColorStats();
void serializeMultiColorStats();

#endif  // MULTI_COLOR_H
