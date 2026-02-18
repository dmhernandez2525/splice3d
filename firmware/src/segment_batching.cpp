#include "segment_batching.h"
#include "config.h"
namespace {
struct BatchingState {
    SegmentEntry segments[kMaxBatchSegments];
    uint8_t count;
    uint8_t nextIndex;
    BatchStrategy strategy;
    uint16_t originalChanges;
    uint16_t optimizedChanges;
    uint16_t heatingCyclesSaved;
    uint16_t reorderedCount;
};
BatchingState sb;
void swapSegments(uint8_t a, uint8_t b) {
    if (a >= sb.count || b >= sb.count) return;
    SegmentEntry tmp = sb.segments[a];
    sb.segments[a] = sb.segments[b];
    sb.segments[b] = sb.segments[tmp.batchedOrder];
    sb.segments[a].batchedOrder = a;
    sb.segments[b].batchedOrder = b;
}
void groupByMaterial() {
    // Simple insertion sort by material type.
    for (uint8_t i = 1; i < sb.count; i++) {
        SegmentEntry key = sb.segments[i];
        int8_t j = static_cast<int8_t>(i) - 1;
        while (j >= 0 &&
               static_cast<uint8_t>(sb.segments[j].material)
               > static_cast<uint8_t>(key.material)) {
            sb.segments[j + 1] = sb.segments[j];
            j--;
        }
        sb.segments[j + 1] = key;
    }
    for (uint8_t i = 0; i < sb.count; i++) {
        sb.segments[i].batchedOrder = i;
    }
}
void minimizeChanges() {
    // Greedy: walk through and pull same-material segments forward.
    for (uint8_t i = 0; i < sb.count; i++) {
        MaterialType current = sb.segments[i].material;
        for (uint8_t j = i + 1; j < sb.count; j++) {
            if (sb.segments[j].material == current) {
                // Shift segment j into position i+1.
                SegmentEntry tmp = sb.segments[j];
                for (uint8_t k = j; k > i + 1; k--) {
                    sb.segments[k] = sb.segments[k - 1];
                }
                sb.segments[i + 1] = tmp;
                i++;
            }
        }
    }
    for (uint8_t i = 0; i < sb.count; i++) {
        sb.segments[i].batchedOrder = i;
    }
}
uint16_t countChangesInternal() {
    if (sb.count < 2) return 0;
    uint16_t changes = 0;
    for (uint8_t i = 1; i < sb.count; i++) {
        if (sb.segments[i].material != sb.segments[i - 1].material) {
            changes++;
        }
    }
    return changes;
}
}  // namespace
void setupSegmentBatching() {
    sb = {};
    sb.strategy = BatchStrategy::NONE;
    Serial.println(F("BATCH_SEG_INIT"));
}
void updateSegmentBatching() {
    // Batching is passive; reordering happens on demand.
}
uint8_t addSegment(uint16_t segmentId, MaterialType material,
                   uint16_t lengthMm) {
    if (sb.count >= kMaxBatchSegments) return 255;
    SegmentEntry& e = sb.segments[sb.count];
    e.segmentId = segmentId;
    e.material = material;
    e.lengthMm = lengthMm;
    e.originalOrder = sb.count;
    e.batchedOrder = sb.count;
    e.processed = false;
    e.active = true;
    sb.count++;
    Serial.print(F("BATCH_SEG_ADD id="));
    Serial.print(segmentId);
    Serial.print(F(" mat="));
    Serial.println(static_cast<uint8_t>(material));
    return sb.count - 1;
}
bool reorderSegments(BatchStrategy strategy) {
    if (sb.count < 2) return false;
    sb.originalChanges = countChangesInternal();
    sb.strategy = strategy;
    if (strategy == BatchStrategy::GROUP_BY_MATERIAL) {
        groupByMaterial();
    } else if (strategy == BatchStrategy::MINIMIZE_CHANGES
               || strategy == BatchStrategy::MINIMIZE_HEATING) {
        minimizeChanges();
    }
    sb.optimizedChanges = countChangesInternal();
    // Count how many segments moved.
    sb.reorderedCount = 0;
    for (uint8_t i = 0; i < sb.count; i++) {
        if (sb.segments[i].originalOrder != sb.segments[i].batchedOrder) {
            sb.reorderedCount++;
        }
    }
    // Estimate heating cycles saved (one per material change avoided).
    if (sb.originalChanges > sb.optimizedChanges) {
        sb.heatingCyclesSaved =
            sb.originalChanges - sb.optimizedChanges;
    } else {
        sb.heatingCyclesSaved = 0;
    }
    Serial.print(F("BATCH_SEG_REORDER strategy="));
    Serial.print(static_cast<uint8_t>(strategy));
    Serial.print(F(" saved="));
    Serial.println(sb.heatingCyclesSaved);
    return true;
}
SegmentEntry getNextSegment() {
    for (uint8_t i = sb.nextIndex; i < sb.count; i++) {
        if (sb.segments[i].active && !sb.segments[i].processed) {
            sb.nextIndex = i;
            return sb.segments[i];
        }
    }
    return {};
}
bool markSegmentProcessed(uint8_t index) {
    if (index >= sb.count) return false;
    sb.segments[index].processed = true;
    sb.nextIndex = index + 1;
    Serial.print(F("BATCH_SEG_DONE idx="));
    Serial.println(index);
    return true;
}
void clearSegments() {
    sb = {};
    sb.strategy = BatchStrategy::NONE;
    Serial.println(F("BATCH_SEG_CLEAR"));
}
uint8_t getSegmentCount() { return sb.count; }
SegmentEntry getSegmentAt(uint8_t index) {
    if (index >= sb.count) return {};
    return sb.segments[index];
}
BatchStrategy getCurrentStrategy() { return sb.strategy; }
uint16_t countMaterialChanges() { return countChangesInternal(); }
BatchingStats getBatchingStats() {
    BatchingStats stats = {};
    stats.totalSegments = sb.count;
    stats.reorderedSegments = sb.reorderedCount;
    stats.materialChanges = sb.optimizedChanges;
    stats.materialChangesSaved =
        (sb.originalChanges > sb.optimizedChanges)
        ? (sb.originalChanges - sb.optimizedChanges) : 0;
    stats.heatingCyclesSaved = sb.heatingCyclesSaved;
    if (sb.count > 0) {
        stats.reorderRatio =
            static_cast<float>(sb.reorderedCount)
            / static_cast<float>(sb.count);
    }
    return stats;
}
void serializeBatchingStats() {
    BatchingStats stats = getBatchingStats();
    Serial.print(F("BATCH_SEG_STATS total="));
    Serial.print(stats.totalSegments);
    Serial.print(F(" reordered="));
    Serial.print(stats.reorderedSegments);
    Serial.print(F(" changes="));
    Serial.print(stats.materialChanges);
    Serial.print(F(" saved="));
    Serial.print(stats.materialChangesSaved);
    Serial.print(F(" heatSaved="));
    Serial.println(stats.heatingCyclesSaved);
}
