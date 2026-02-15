#include "temperature.h"
#include "config.h"
#include <PID_v1.h>
#include <math.h>
namespace {
constexpr uint8_t kThermistorSamples = 5;
struct MaterialProfileEntry {
    MaterialProfile id;
    float spliceTargetC;
    float minMotionC;
    float rampRateCPerSec;
    uint16_t soakTimeMs;
};
constexpr MaterialProfileEntry kProfiles[] = {
    {MaterialProfile::PLA,  210.0f, 180.0f, 2.0f, 2000},
    {MaterialProfile::PETG, 235.0f, 210.0f, 1.5f, 3000},
    {MaterialProfile::ABS,  250.0f, 220.0f, 1.0f, 4000},
};
constexpr uint8_t kProfileCount = sizeof(kProfiles) / sizeof(kProfiles[0]);
double pidInput = 0.0;
double pidOutput = 0.0;
double pidSetpoint = 0.0;
double Kp = 20.0;
double Ki = 1.0;
double Kd = 5.0;
PID heaterPID(&pidInput, &pidOutput, &pidSetpoint, Kp, Ki, Kd, DIRECT);
struct TempState {
    float currentC;
    float targetC;
    float effectiveSetpointC;
    float pidOutputPwm;
    MaterialProfile material;
    HeatingStage stage;
    bool pidEnabled;
    bool thermalFault;
    bool autoTuneActive;
    uint32_t lastReadMs;
    uint32_t lastLogMs;
    uint32_t lastPidRunMs;
    uint32_t stageEnteredMs;
    float runawayBaselineC;
    uint32_t lastRunawayCheckMs;
    uint8_t fanPwm;
};
TempState st = {
    0.0f, 0.0f, 0.0f, 0.0f,
    MaterialProfile::PLA, HeatingStage::OFF,
    false, false, false,
    0, 0, 0, 0,
    0.0f, 0,
    0,
};
const MaterialProfileEntry& activeProfileEntry() {
    for (uint8_t i = 0; i < kProfileCount; ++i) {
        if (kProfiles[i].id == st.material) return kProfiles[i];
    }
    return kProfiles[0];
}
float readThermistorRaw() {
    float sum = 0.0f;
    for (uint8_t i = 0; i < kThermistorSamples; ++i) {
        sum += static_cast<float>(analogRead(THERMISTOR_PIN));
    }
    const float avg = sum / static_cast<float>(kThermistorSamples);
    if (avg <= 1.0f || avg >= 1022.0f) return -999.0f;
    const float resistance = static_cast<float>(THERMISTOR_SERIES_R) / (1023.0f / avg - 1.0f);
    float steinhart = resistance / static_cast<float>(THERMISTOR_NOMINAL_R);
    steinhart = logf(steinhart);
    steinhart /= static_cast<float>(THERMISTOR_B_COEFF);
    steinhart += 1.0f / (static_cast<float>(THERMISTOR_NOMINAL_T) + 273.15f);
    steinhart = 1.0f / steinhart;
    steinhart -= 273.15f;
    return steinhart;
}
bool isThermistorValid(float tempC) {
    return tempC > THERMISTOR_DISCONNECT_LOW_C && tempC < THERMISTOR_DISCONNECT_HIGH_C;
}
void enterFault(const char* reason) {
    st.thermalFault = true;
    st.pidEnabled = false;
    st.stage = HeatingStage::FAULT;
    heaterPID.SetMode(MANUAL);
    analogWrite(HEATER_PIN, 0);
    digitalWrite(COOLING_FAN_PIN, HIGH);
    Serial.print(F("THERMAL_FAULT "));
    Serial.println(reason);
}
void checkThermalRunaway(uint32_t nowMs) {
    if (!st.pidEnabled || st.thermalFault) return;
    if (nowMs - st.lastRunawayCheckMs < THERMAL_RUNAWAY_CHECK_INTERVAL_MS) return;
    st.lastRunawayCheckMs = nowMs;
    if (st.currentC < st.targetC - static_cast<float>(TEMP_HYSTERESIS)) {
        const float rise = st.currentC - st.runawayBaselineC;
        const float elapsed = static_cast<float>(nowMs - st.stageEnteredMs) / 1000.0f;
        const float requiredRise = THERMAL_RUNAWAY_MIN_RISE_C;
        if (elapsed > (static_cast<float>(THERMAL_RUNAWAY_PERIOD_MS) / 1000.0f) && rise < requiredRise) {
            enterFault("RUNAWAY");
            return;
        }
    }
    st.runawayBaselineC = st.currentC;
}
void updateHeatingStage(uint32_t nowMs) {
    if (st.thermalFault || !st.pidEnabled) return;
    const float target = st.targetC;
    const float current = st.currentC;
    const float hysteresis = static_cast<float>(TEMP_HYSTERESIS);
    switch (st.stage) {
        case HeatingStage::OFF:
            if (target > 0.0f) {
                st.stage = HeatingStage::PREHEAT;
                st.stageEnteredMs = nowMs;
                st.runawayBaselineC = current;
            }
            break;
        case HeatingStage::PREHEAT:
            if (current >= target - hysteresis) {
                st.stage = HeatingStage::SOAK;
                st.stageEnteredMs = nowMs;
            }
            break;
        case HeatingStage::SOAK: {
            const uint32_t soakMs = activeProfileEntry().soakTimeMs;
            if (nowMs - st.stageEnteredMs >= soakMs && current >= target - hysteresis) {
                st.stage = HeatingStage::READY;
                st.stageEnteredMs = nowMs;
            }
            if (current < target - hysteresis * 2.0f) {
                st.stage = HeatingStage::PREHEAT;
                st.stageEnteredMs = nowMs;
            }
            break;
        }
        case HeatingStage::READY:
            if (current < target - hysteresis * 2.0f) {
                st.stage = HeatingStage::PREHEAT;
                st.stageEnteredMs = nowMs;
            }
            break;
        case HeatingStage::FAULT:
            break;
    }
}
void computeRampSetpoint(uint32_t nowMs) {
    if (!st.pidEnabled || st.thermalFault) {
        st.effectiveSetpointC = 0.0f;
        return;
    }
    const float ramp = activeProfileEntry().rampRateCPerSec;
    const float elapsed = static_cast<float>(nowMs - st.stageEnteredMs) / 1000.0f;
    const float ramped = st.runawayBaselineC + ramp * elapsed;
    st.effectiveSetpointC = fminf(ramped, st.targetC);
    pidSetpoint = static_cast<double>(st.effectiveSetpointC);
}
void logTemperature(uint32_t nowMs) {
    if (nowMs - st.lastLogMs < TEMP_LOG_INTERVAL_MS) return;
    st.lastLogMs = nowMs;
    Serial.print(F("TEMP_LOG C="));
    Serial.print(st.currentC, 1);
    Serial.print(F(" T="));
    Serial.print(st.targetC, 1);
    Serial.print(F(" S="));
    Serial.print(st.effectiveSetpointC, 1);
    Serial.print(F(" PWM="));
    Serial.print(st.pidOutputPwm, 0);
    Serial.print(F(" STAGE="));
    Serial.println(static_cast<uint8_t>(st.stage));
}
}  // namespace
void setupTemperature() {
    pinMode(HEATER_PIN, OUTPUT);
    digitalWrite(HEATER_PIN, LOW);
    pinMode(COOLING_FAN_PIN, OUTPUT);
    digitalWrite(COOLING_FAN_PIN, LOW);
    pinMode(THERMISTOR_PIN, INPUT);
    heaterPID.SetMode(MANUAL);
    heaterPID.SetOutputLimits(0, 255);
    heaterPID.SetSampleTime(100);
}
void updateTemperature() {
    const uint32_t nowMs = millis();
    if (nowMs - st.lastReadMs >= 100) {
        st.currentC = readThermistorRaw();
        st.lastReadMs = nowMs;
        if (!isThermistorValid(st.currentC)) { enterFault("THERMISTOR"); return; }
        if (st.currentC > static_cast<float>(MAX_TEMP)) { enterFault("OVERTEMP"); return; }
    }
    checkThermalRunaway(nowMs);
    updateHeatingStage(nowMs);
    computeRampSetpoint(nowMs);
    if (st.pidEnabled && !st.thermalFault) {
        pidInput = static_cast<double>(st.currentC);
        heaterPID.Compute();
        st.pidOutputPwm = static_cast<float>(pidOutput);
        analogWrite(HEATER_PIN, static_cast<int>(pidOutput));
        st.lastPidRunMs = nowMs;
    }
    if (st.pidEnabled && (nowMs - st.lastPidRunMs > PID_WATCHDOG_MS) && st.lastPidRunMs > 0) {
        enterFault("PID_WATCHDOG");
    }
    updatePidAutoTune();
    logTemperature(nowMs);
}
void setTargetTemperature(float tempC) {
    if (tempC > static_cast<float>(MAX_TEMP)) tempC = static_cast<float>(MAX_TEMP);
    st.targetC = tempC;
    pidSetpoint = static_cast<double>(tempC);
    if (tempC > 0.0f) {
        st.pidEnabled = true;
        st.thermalFault = false;
        heaterPID.SetMode(AUTOMATIC);
        if (st.stage == HeatingStage::OFF || st.stage == HeatingStage::FAULT) {
            st.stage = HeatingStage::PREHEAT;
            st.stageEnteredMs = millis();
            st.runawayBaselineC = st.currentC;
            st.lastRunawayCheckMs = millis();
        }
    } else {
        st.pidEnabled = false;
        heaterPID.SetMode(MANUAL);
        analogWrite(HEATER_PIN, 0);
        st.stage = HeatingStage::OFF;
    }
}
void setMaterialProfile(MaterialProfile profile) {
    st.material = profile;
    const MaterialProfileEntry& entry = activeProfileEntry();
    setTargetTemperature(entry.spliceTargetC);
}
MaterialProfile getMaterialProfile() { return st.material; }
TemperatureProfile getActiveTemperatureProfile() {
    const MaterialProfileEntry& e = activeProfileEntry();
    return {e.id, e.spliceTargetC, e.minMotionC, e.rampRateCPerSec, e.soakTimeMs};
}
float getCurrentTemperature() { return st.currentC; }
float getTargetTemperature() { return st.targetC; }
void setHeaterPower(uint8_t power) {
    st.pidEnabled = false;
    heaterPID.SetMode(MANUAL);
    analogWrite(HEATER_PIN, power);
    st.pidOutputPwm = static_cast<float>(power);
}
void setCoolingFan(bool on) {
    st.fanPwm = on ? 255 : 0;
    analogWrite(COOLING_FAN_PIN, st.fanPwm);
}
void setCoolingFanPwm(uint8_t pwm) {
    st.fanPwm = pwm;
    analogWrite(COOLING_FAN_PIN, pwm);
}
bool isTemperatureReached() {
    return st.currentC >= st.targetC - static_cast<float>(TEMP_HYSTERESIS);
}
bool isColdExtrusionBlocked() {
    return st.currentC < COLD_EXTRUSION_MIN_C && st.targetC > 0.0f;
}
bool hasThermalFault() { return st.thermalFault; }
void setPidTunings(float kp, float ki, float kd) {
    Kp = static_cast<double>(kp);
    Ki = static_cast<double>(ki);
    Kd = static_cast<double>(kd);
    heaterPID.SetTunings(Kp, Ki, Kd);
}
HeatingStage getHeatingStage() { return st.stage; }
float predictTimeToTargetSeconds() {
    if (st.targetC <= 0.0f || st.currentC >= st.targetC) return 0.0f;
    const float delta = st.targetC - st.currentC;
    const float rate = activeProfileEntry().rampRateCPerSec;
    if (rate <= 0.0f) return 999.0f;
    return delta / rate;
}
TemperatureTelemetry getTemperatureTelemetry() {
    return {
        st.currentC, st.targetC, st.effectiveSetpointC,
        predictTimeToTargetSeconds(), st.pidOutputPwm,
        st.autoTuneActive, st.thermalFault, st.stage,
    };
}
