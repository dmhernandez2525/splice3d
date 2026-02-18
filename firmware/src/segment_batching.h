/**
 * Splice3D Segment Batching (F6.1).
 *
 * Optimizes splice ordering for minimal material changes and heating
 * cycles. Groups consecutive same-material segments, tracks reorder
 * statistics, and provides batch reordering APIs.
 */

#ifndef SEGMENT_BATCHING_H
#define SEGMENT_BATCHING_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxBatchSegments = 32;

enum class BatchStrategy : uint8_t {
    NONE = 0,
    GROUP_BY_MATERIAL,
    MINIMIZE_CHANGES,
    MINIMIZE_HEATING,
};

struct SegmentEntry {
    uint16_t segmentId;
    MaterialType material;
    uint16_t lengthMm;
    uint8_t originalOrder;
    uint8_t batchedOrder;
    bool processed;
    bool active;
};

struct BatchingStats {
    uint16_t totalSegments;
    uint16_t reorderedSegments;
    uint16_t materialChanges;
    uint16_t materialChangesSaved;
    uint16_t heatingCyclesSaved;
    float reorderRatio;
};

void setupSegmentBatching();
void updateSegmentBatching();

// Add a segment to the batch queue. Returns index or 255.
uint8_t addSegment(uint16_t segmentId, MaterialType material,
                   uint16_t lengthMm);

// Reorder segments using the given strategy.
bool reorderSegments(BatchStrategy strategy);

// Get the next segment to process (in batched order).
SegmentEntry getNextSegment();

// Mark a segment as processed.
bool markSegmentProcessed(uint8_t index);

// Clear all segments.
void clearSegments();

// Query APIs.
uint8_t getSegmentCount();
SegmentEntry getSegmentAt(uint8_t index);
BatchStrategy getCurrentStrategy();

// Statistics.
BatchingStats getBatchingStats();
void serializeBatchingStats();

// Count material changes in current ordering.
uint16_t countMaterialChanges();

#endif  // SEGMENT_BATCHING_H
