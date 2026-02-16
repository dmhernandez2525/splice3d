/**
 * Splice3D 8+ Color Input Channel Support (F10.2).
 *
 * Multi-channel filament management with input selection, switching coordination, per-channel stats.
 */

#ifndef MULTI_COLOR_H
#define MULTI_COLOR_H

#include <Arduino.h>

constexpr uint8_t kMaxColorChannels = 8;
constexpr uint8_t kMaxSwitchQueue = 16;
enum class ChannelState : uint8_t {
    EMPTY = 0,
    LOADED = 1,
    ACTIVE = 2,
    SWITCHING = 3,
    ERROR = 4,
    MAINTENANCE = 5,
};

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
