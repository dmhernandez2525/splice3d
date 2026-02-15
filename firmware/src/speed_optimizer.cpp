#include "speed_optimizer.h"
#include "config.h"
namespace {
struct SpeedState {
    ParallelOp ops[kMaxParallelOps];
    uint8_t opCount;
    CycleBreakdown cycles[kMaxCycleRecords];
    uint8_t cycleCount;
    uint8_t cycleRing;
    CycleBreakdown current;
    bool cycleActive;
    uint32_t totalOverlapMs;
    uint32_t bestMs;
    uint32_t worstMs;
    uint32_t totalCycleMs;
    uint16_t completedCycles;
};
SpeedState ss;
// Overlap rules: heating+feeding, cooling+positioning.
bool overlapAllowed(OpType a, OpType b) {
    if (a == b) return false;
    bool heatFeed =
        (a == OpType::HEATING && b == OpType::FEEDING)
        || (a == OpType::FEEDING && b == OpType::HEATING);
    bool coolPos =
        (a == OpType::COOLING && b == OpType::POSITIONING)
        || (a == OpType::POSITIONING && b == OpType::COOLING);
    bool heatPos =
        (a == OpType::HEATING && b == OpType::POSITIONING)
        || (a == OpType::POSITIONING && b == OpType::HEATING);
    return heatFeed || coolPos || heatPos;
}
void recordOpDuration(OpType type, uint32_t durationMs) {
    if (!ss.cycleActive) return;
    uint8_t idx = static_cast<uint8_t>(type);
    if (idx >= static_cast<uint8_t>(OpType::OP_TYPE_COUNT)) return;
    uint32_t* fields[] = {
        &ss.current.heatingMs,
        &ss.current.feedingMs,
        &ss.current.cuttingMs,
        &ss.current.splicingMs,
        &ss.current.coolingMs,
        &ss.current.positioningMs,
    };
    *fields[idx] += durationMs;
}
}  // namespace
void setupSpeedOptimizer() {
    ss = {};
    ss.bestMs = 0xFFFFFFFF;
    Serial.println(F("SPEED_OPT_INIT"));
}
void updateSpeedOptimizer() {
    // Check for operations that can be overlapped.
    for (uint8_t i = 0; i < ss.opCount; i++) {
        if (ss.ops[i].state != OpState::RUNNING) continue;
        for (uint8_t j = i + 1; j < ss.opCount; j++) {
            if (ss.ops[j].state != OpState::RUNNING) continue;
            if (overlapAllowed(ss.ops[i].type, ss.ops[j].type)) {
                ss.ops[i].overlapped = true;
                ss.ops[j].overlapped = true;
            }
        }
    }
}
uint8_t startParallelOp(OpType type) {
    if (ss.opCount >= kMaxParallelOps) return 255;
    ParallelOp& op = ss.ops[ss.opCount];
    op.type = type;
    op.state = OpState::RUNNING;
    op.startTimeMs = millis();
    op.overlapped = false;
    op.active = true;
    ss.opCount++;
    Serial.print(F("SPEED_OP_START type="));
    Serial.print(static_cast<uint8_t>(type));
    Serial.print(F(" idx="));
    Serial.println(ss.opCount - 1);
    return ss.opCount - 1;
}
bool completeParallelOp(uint8_t index) {
    if (index >= ss.opCount) return false;
    ParallelOp& op = ss.ops[index];
    if (op.state != OpState::RUNNING) return false;
    op.state = OpState::COMPLETED;
    op.endTimeMs = millis();
    op.durationMs = op.endTimeMs - op.startTimeMs;
    recordOpDuration(op.type, op.durationMs);
    if (op.overlapped) {
        ss.totalOverlapMs += op.durationMs;
        if (ss.cycleActive) {
            ss.current.overlapSavedMs += op.durationMs;
        }
    }
    Serial.print(F("SPEED_OP_DONE idx="));
    Serial.print(index);
    Serial.print(F(" ms="));
    Serial.print(op.durationMs);
    Serial.print(F(" overlap="));
    Serial.println(op.overlapped ? F("Y") : F("N"));
    return true;
}
bool cancelParallelOp(uint8_t index) {
    if (index >= ss.opCount) return false;
    if (ss.ops[index].state != OpState::RUNNING) return false;
    ss.ops[index].state = OpState::CANCELLED;
    ss.ops[index].endTimeMs = millis();
    Serial.print(F("SPEED_OP_CANCEL idx="));
    Serial.println(index);
    return true;
}
bool canOverlap(OpType a, OpType b) {
    return overlapAllowed(a, b);
}
void startCycle(uint16_t cycleId) {
    if (ss.cycleActive) return;
    ss.current = {};
    ss.current.cycleId = cycleId;
    ss.cycleActive = true;
    // Reset ops for new cycle.
    ss.opCount = 0;
    Serial.print(F("SPEED_CYCLE_START id="));
    Serial.println(cycleId);
}
void completeCycle() {
    if (!ss.cycleActive) return;
    ss.current.totalMs =
        ss.current.heatingMs + ss.current.feedingMs
        + ss.current.cuttingMs + ss.current.splicingMs
        + ss.current.coolingMs + ss.current.positioningMs
        - ss.current.overlapSavedMs;
    ss.current.complete = true;
    ss.cycleActive = false;
    // Store in ring buffer.
    ss.cycles[ss.cycleRing] = ss.current;
    ss.cycleRing = (ss.cycleRing + 1) % kMaxCycleRecords;
    if (ss.cycleCount < kMaxCycleRecords) ss.cycleCount++;
    // Update aggregate stats.
    ss.completedCycles++;
    ss.totalCycleMs += ss.current.totalMs;
    if (ss.current.totalMs < ss.bestMs) {
        ss.bestMs = ss.current.totalMs;
    }
    if (ss.current.totalMs > ss.worstMs) {
        ss.worstMs = ss.current.totalMs;
    }
    Serial.print(F("SPEED_CYCLE_DONE id="));
    Serial.print(ss.current.cycleId);
    Serial.print(F(" total="));
    Serial.print(ss.current.totalMs);
    Serial.print(F(" saved="));
    Serial.println(ss.current.overlapSavedMs);
}
CycleBreakdown getCurrentCycle() { return ss.current; }
uint8_t getCycleRecordCount() { return ss.cycleCount; }
CycleBreakdown getCycleRecord(uint8_t index) {
    if (index >= ss.cycleCount) return {};
    return ss.cycles[index];
}
void clearSpeedData() {
    ss = {};
    ss.bestMs = 0xFFFFFFFF;
    Serial.println(F("SPEED_CLEAR"));
}
uint8_t getActiveOpCount() {
    uint8_t active = 0;
    for (uint8_t i = 0; i < ss.opCount; i++) {
        if (ss.ops[i].state == OpState::RUNNING) active++;
    }
    return active;
}
ParallelOp getParallelOp(uint8_t index) {
    if (index >= ss.opCount) return {};
    return ss.ops[index];
}
SpeedOptimizerStats getSpeedStats() {
    SpeedOptimizerStats stats = {};
    stats.totalCycles = ss.completedCycles;
    stats.totalOverlapSavedMs = ss.totalOverlapMs;
    stats.parallelOpsCount = ss.opCount;
    if (ss.completedCycles > 0) {
        stats.avgCycleMs = ss.totalCycleMs / ss.completedCycles;
        stats.bestCycleMs = ss.bestMs;
        stats.worstCycleMs = ss.worstMs;
        if (ss.totalCycleMs > 0) {
            stats.overlapRatio =
                static_cast<float>(ss.totalOverlapMs)
                / static_cast<float>(ss.totalCycleMs);
        }
    }
    return stats;
}
void serializeSpeedStats() {
    SpeedOptimizerStats stats = getSpeedStats();
    Serial.print(F("SPEED_STATS cycles="));
    Serial.print(stats.totalCycles);
    Serial.print(F(" avg="));
    Serial.print(stats.avgCycleMs);
    Serial.print(F(" best="));
    Serial.print(stats.bestCycleMs);
    Serial.print(F(" worst="));
    Serial.print(stats.worstCycleMs);
    Serial.print(F(" saved="));
    Serial.print(stats.totalOverlapSavedMs);
    Serial.print(F(" overlap="));
    Serial.println(stats.overlapRatio, 2);
}
