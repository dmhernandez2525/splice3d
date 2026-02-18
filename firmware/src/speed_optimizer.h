/**
 * Splice3D Speed Optimization (F6.4).
 *
 * Parallel operation scheduling for splice cycles. Overlaps heating
 * with feeding, pre-positions next filament during cooling, and
 * tracks cycle time breakdowns for continuous improvement.
 */

#ifndef SPEED_OPTIMIZER_H
#define SPEED_OPTIMIZER_H

#include <Arduino.h>

constexpr uint8_t kMaxParallelOps = 8;
constexpr uint8_t kMaxCycleRecords = 16;

enum class OpType : uint8_t {
    HEATING = 0,
    FEEDING,
    CUTTING,
    SPLICING,
    COOLING,
    POSITIONING,
    OP_TYPE_COUNT,
};

enum class OpState : uint8_t {
    PENDING = 0,
    RUNNING,
    COMPLETED,
    CANCELLED,
};

struct ParallelOp {
    OpType type;
    OpState state;
    uint32_t startTimeMs;
    uint32_t endTimeMs;
    uint32_t durationMs;
    bool overlapped;
    bool active;
};

struct CycleBreakdown {
    uint32_t heatingMs;
    uint32_t feedingMs;
    uint32_t cuttingMs;
    uint32_t splicingMs;
    uint32_t coolingMs;
    uint32_t positioningMs;
    uint32_t totalMs;
    uint32_t overlapSavedMs;
    uint16_t cycleId;
    bool complete;
};

struct SpeedOptimizerStats {
    uint16_t totalCycles;
    uint32_t avgCycleMs;
    uint32_t bestCycleMs;
    uint32_t worstCycleMs;
    uint32_t totalOverlapSavedMs;
    uint16_t parallelOpsCount;
    float overlapRatio;
};

void setupSpeedOptimizer();
void updateSpeedOptimizer();

// Start a parallel operation. Returns index or 255.
uint8_t startParallelOp(OpType type);

// Complete a parallel operation.
bool completeParallelOp(uint8_t index);

// Cancel a parallel operation.
bool cancelParallelOp(uint8_t index);

// Check if two operations can overlap.
bool canOverlap(OpType a, OpType b);

// Start a new splice cycle.
void startCycle(uint16_t cycleId);

// Complete the current cycle.
void completeCycle();

// Get current cycle breakdown.
CycleBreakdown getCurrentCycle();

// Get historical cycle data.
uint8_t getCycleRecordCount();
CycleBreakdown getCycleRecord(uint8_t index);

// Clear operation and cycle data.
void clearSpeedData();

// Query active operations.
uint8_t getActiveOpCount();
ParallelOp getParallelOp(uint8_t index);

// Statistics.
SpeedOptimizerStats getSpeedStats();
void serializeSpeedStats();

#endif  // SPEED_OPTIMIZER_H
