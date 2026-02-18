#include "telemetry_stream.h"
#include "config.h"
#include "temperature.h"
#include "encoder_system.h"
#include "stepper_control.h"
#include "splice_execution.h"
#include "position_tracking.h"
#include "error_handler.h"
#include "error_recovery.h"
#include "state_machine.h"
extern StateMachine stateMachine;
namespace {
constexpr uint32_t kDefaultIntervalMs = 1000UL;
constexpr uint32_t kHeartbeatIntervalMs = 5000UL;
constexpr uint32_t kMinIntervalMs = 100UL;
struct TelState {
    StreamConfig cfg;
    uint32_t lastStreamMs;
    uint32_t lastHeartbeatMs;
    uint32_t heartbeatCount;
    bool heartbeatEnabled;
};
TelState ts;
void printJsonKV(const __FlashStringHelper* key, float val, bool comma) {
    Serial.print('"');
    Serial.print(key);
    Serial.print(F("\":"));
    Serial.print(val, 2);
    if (comma) Serial.print(',');
}
void printJsonKV(const __FlashStringHelper* key, uint32_t val, bool comma) {
    Serial.print('"');
    Serial.print(key);
    Serial.print(F("\":"));
    Serial.print(val);
    if (comma) Serial.print(',');
}
void printJsonKV(const __FlashStringHelper* key, const char* val, bool comma) {
    Serial.print('"');
    Serial.print(key);
    Serial.print(F("\":\""));
    Serial.print(val);
    Serial.print('"');
    if (comma) Serial.print(',');
}
void printJsonKV(const __FlashStringHelper* key, bool val, bool comma) {
    Serial.print('"');
    Serial.print(key);
    Serial.print(F("\":"));
    Serial.print(val ? F("true") : F("false"));
    if (comma) Serial.print(',');
}
void emitSummary() {
    Serial.print(F("{\"type\":\"telemetry\","));
    Serial.print(F("\"t\":"));
    Serial.print(millis());
    Serial.print(',');
    printJsonKV(F("state"), stateMachine.getStateString(), true);
    printJsonKV(F("temp"), getCurrentTemperature(), true);
    printJsonKV(F("target"), getTargetTemperature(), true);
    const EncoderTelemetry enc = getEncoderTelemetry();
    printJsonKV(F("pos_mm"), enc.positionMm, true);
    printJsonKV(F("vel"), enc.velocityMmPerSec, true);
    printJsonKV(F("slip"), enc.slipDetected, true);
    const SpliceTelemetry sp = getSpliceTelemetry();
    printJsonKV(F("splice_active"), isSpliceActive(), true);
    printJsonKV(F("quality"), sp.qualityScore, true);
    printJsonKV(F("error"), errorHandler.hasError(), false);
    Serial.println('}');
}
void emitVerbose() {
    Serial.print(F("{\"type\":\"telemetry_v\","));
    Serial.print(F("\"t\":"));
    Serial.print(millis());
    Serial.print(',');
    // State.
    printJsonKV(F("state"), stateMachine.getStateString(), true);
    // Temperature.
    Serial.print(F("\"temp\":{"));
    printJsonKV(F("current"), getCurrentTemperature(), true);
    printJsonKV(F("target"), getTargetTemperature(), true);
    printJsonKV(F("stage"), static_cast<uint32_t>(getHeatingStage()), true);
    printJsonKV(F("fault"), hasThermalFault(), false);
    Serial.print(F("},"));
    // Encoder.
    if (ts.cfg.includeEncoder) {
        const EncoderTelemetry enc = getEncoderTelemetry();
        Serial.print(F("\"enc\":{"));
        printJsonKV(F("mm"), enc.positionMm, true);
        printJsonKV(F("vel"), enc.velocityMmPerSec, true);
        printJsonKV(F("slip_mm"), enc.slipErrorMm, true);
        printJsonKV(F("slip"), enc.slipDetected, false);
        Serial.print(F("},"));
    }
    // Motors.
    if (ts.cfg.includeMotors) {
        const MotorPosition mA = getMotorPosition(MotorAxis::FEED_A);
        const MotorPosition mB = getMotorPosition(MotorAxis::FEED_B);
        Serial.print(F("\"motors\":{"));
        printJsonKV(F("a_mm"), mA.absoluteMm, true);
        printJsonKV(F("b_mm"), mB.absoluteMm, false);
        Serial.print(F("},"));
    }
    // Splice.
    const SpliceTelemetry sp = getSpliceTelemetry();
    Serial.print(F("\"splice\":{"));
    printJsonKV(F("active"), isSpliceActive(), true);
    printJsonKV(F("elapsed"), sp.elapsedMs, true);
    printJsonKV(F("remaining"), sp.estimatedRemainingMs, true);
    printJsonKV(F("quality"), sp.qualityScore, false);
    Serial.print(F("},"));
    // Position tracking.
    const PositionSnapshot snap = getPositionSnapshot();
    Serial.print(F("\"pos\":{"));
    printJsonKV(F("drift"), snap.driftMm, true);
    printJsonKV(F("cum_drift"), snap.cumulativeDriftMm, false);
    Serial.print(F("},"));
    // Recovery.
    if (ts.cfg.includeRecovery) {
        Serial.print(F("\"recovery\":{"));
        printJsonKV(F("active"), isRecoveryActive(), true);
        printJsonKV(F("phase"), static_cast<uint32_t>(getRecoveryPhase()), false);
        Serial.print(F("},"));
    }
    // Error.
    printJsonKV(F("error"), errorHandler.hasError(), false);
    Serial.println('}');
}
void emitHeartbeat() {
    ts.heartbeatCount++;
    Serial.print(F("{\"type\":\"heartbeat\",\"t\":"));
    Serial.print(millis());
    Serial.print(F(",\"seq\":"));
    Serial.print(ts.heartbeatCount);
    Serial.println('}');
}
}  // namespace
void setupTelemetryStream() {
    ts = {};
    ts.cfg.mode = StreamMode::OFF;
    ts.cfg.intervalMs = kDefaultIntervalMs;
    ts.cfg.includeMotors = true;
    ts.cfg.includeEncoder = true;
    ts.cfg.includeRecovery = true;
    ts.heartbeatEnabled = false;
}
void updateTelemetryStream() {
    const uint32_t now = millis();
    // Telemetry stream.
    if (ts.cfg.mode != StreamMode::OFF) {
        if (now - ts.lastStreamMs >= ts.cfg.intervalMs) {
            ts.lastStreamMs = now;
            if (ts.cfg.mode == StreamMode::SUMMARY) {
                emitSummary();
            } else {
                emitVerbose();
            }
        }
    }
    // Heartbeat.
    if (ts.heartbeatEnabled && now - ts.lastHeartbeatMs >= kHeartbeatIntervalMs) {
        ts.lastHeartbeatMs = now;
        emitHeartbeat();
    }
}
void setStreamMode(StreamMode mode) { ts.cfg.mode = mode; }
StreamMode getStreamMode() { return ts.cfg.mode; }
void setStreamInterval(uint32_t intervalMs) {
    if (intervalMs < kMinIntervalMs) intervalMs = kMinIntervalMs;
    ts.cfg.intervalMs = intervalMs;
}
uint32_t getStreamInterval() { return ts.cfg.intervalMs; }
void setStreamConfig(const StreamConfig& cfg) { ts.cfg = cfg; }
StreamConfig getStreamConfig() { return ts.cfg; }
void enableHeartbeat(bool enabled) { ts.heartbeatEnabled = enabled; }
bool isHeartbeatEnabled() { return ts.heartbeatEnabled; }
uint32_t getHeartbeatCount() { return ts.heartbeatCount; }
void emitStatusReport() { emitVerbose(); }
