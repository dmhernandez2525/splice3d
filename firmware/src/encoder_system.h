/**
 * Splice3D encoder subsystem.
 *
 * Handles quadrature decoding, calibration persistence, slip detection,
 * closed-loop correction, and telemetry logging.
 */

#ifndef ENCODER_SYSTEM_H
#define ENCODER_SYSTEM_H

#include <Arduino.h>

struct EncoderTelemetry {
    int64_t ticks;
    float positionMm;
    float velocityMmPerSec;
    float slipErrorMm;
    float averageSlipErrorMm;
    bool slipDetected;
};

struct EncoderHealth {
    uint32_t validTransitions;
    uint32_t invalidTransitions;
    float signalQuality;
    bool degraded;
    bool failed;
    uint32_t correctionEvents;
    uint32_t calibrationRuns;
};

void setupEncoderSystem();
void updateEncoderSystem();

EncoderTelemetry getEncoderTelemetry();
EncoderHealth getEncoderHealth();

bool beginEncoderCalibration(float knownLengthMm);
bool completeEncoderCalibration();
bool isEncoderCalibrationActive();

bool saveEncoderCalibration();
bool loadEncoderCalibration();
void resetEncoderCounters();

bool setEncoderTicksPerMm(float ticksPerMm);
float getEncoderTicksPerMm();

void setEncoderLogIntervalMs(uint32_t intervalMs);
uint32_t getEncoderLogIntervalMs();

void setEncoderClosedLoopEnabled(bool enabled);
bool isEncoderClosedLoopEnabled();

#endif  // ENCODER_SYSTEM_H
