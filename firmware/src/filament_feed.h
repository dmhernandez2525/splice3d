/**
 * Splice3D Filament Feeding System (F3.1).
 *
 * Coordinates dual-input motor feeding, tension control via encoder feedback,
 * runout detection, jam detection, and feed statistics.
 */

#ifndef FILAMENT_FEED_H
#define FILAMENT_FEED_H

#include <Arduino.h>

enum class FeedMode : uint8_t {
    IDLE = 0,
    FEED_A = 1,
    FEED_B = 2,
    RETRACT_A = 3,
    RETRACT_B = 4,
    DRY_RUN = 5,
    LOADING = 6,
};

struct FeedStatistics {
    float totalFedMmA;
    float totalFedMmB;
    float averageFeedRate;
    uint32_t jamCount;
    uint32_t slipEvents;
    uint32_t runoutEvents;
};

struct FeedConfig {
    float fastSpeedMmS;
    float slowSpeedMmS;
    float retractSpeedMmS;
    float jamThresholdMmS;
    float tensionMinMmS;
    float tensionMaxMmS;
    uint32_t jamDetectionWindowMs;
};

void setupFilamentFeed();
void updateFilamentFeed();

bool startFeed(uint8_t input, float lengthMm);
bool startRetract(uint8_t input, float lengthMm);
bool startDryRunFeed(uint8_t input, float lengthMm);
void abortFeed();

bool isFeedActive();
bool isFeedComplete();
FeedMode getFeedMode();
FeedStatistics getFeedStatistics();
FeedConfig getFeedConfig();

bool isFilamentRunout(uint8_t input);
bool isJamDetected();

void setFeedSpeeds(float fastMmS, float slowMmS, float retractMmS);
void setJamThreshold(float thresholdMmS);
void resetFeedStatistics();

#endif  // FILAMENT_FEED_H
