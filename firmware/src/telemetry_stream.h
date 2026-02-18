/**
 * Splice3D Telemetry Streaming (F4.1).
 *
 * Provides periodic JSON telemetry output, heartbeat keep-alive,
 * and structured status reporting for host integration.
 */

#ifndef TELEMETRY_STREAM_H
#define TELEMETRY_STREAM_H

#include <Arduino.h>

enum class StreamMode : uint8_t {
    OFF = 0,
    SUMMARY,
    VERBOSE,
};

struct StreamConfig {
    StreamMode mode;
    uint32_t intervalMs;
    bool includeMotors;
    bool includeEncoder;
    bool includeRecovery;
};

void setupTelemetryStream();
void updateTelemetryStream();

// Control streaming.
void setStreamMode(StreamMode mode);
StreamMode getStreamMode();
void setStreamInterval(uint32_t intervalMs);
uint32_t getStreamInterval();
void setStreamConfig(const StreamConfig& cfg);
StreamConfig getStreamConfig();

// Heartbeat.
void enableHeartbeat(bool enabled);
bool isHeartbeatEnabled();
uint32_t getHeartbeatCount();

// One-shot report.
void emitStatusReport();

#endif  // TELEMETRY_STREAM_H
