/**
 * TMC2209 UART Driver Configuration Implementation
 */

#include "tmc_config.h"
#include "config.h"

#ifdef TMC_UART_ENABLED

// Define driver instances with addresses
TMC2209Stepper tmc_x(&SERIAL_PORT, R_SENSE, TMC_X_ADDR);
TMC2209Stepper tmc_y(&SERIAL_PORT, R_SENSE, TMC_Y_ADDR);
TMC2209Stepper tmc_z(&SERIAL_PORT, R_SENSE, TMC_Z_ADDR);
TMC2209Stepper tmc_e(&SERIAL_PORT, R_SENSE, TMC_E_ADDR);

void initTMCDrivers() {
    // Initialize UART at 115200 baud (TMC default)
    SERIAL_PORT.begin(115200);
    
    // Small delay for drivers to initialize
    delay(100);
    
    // Configure each driver
    configureTMCDriver(tmc_x, MOTOR_CURRENT_MA, true);
    configureTMCDriver(tmc_y, MOTOR_CURRENT_MA, true);
    configureTMCDriver(tmc_z, MOTOR_CURRENT_MA, true);
    configureTMCDriver(tmc_e, MOTOR_CURRENT_MA, true);
    
    Serial.println("TMC2209 drivers initialized");
    
    // Check status
    if (checkDriverStatus()) {
        Serial.println("All drivers OK");
    } else {
        Serial.println("WARNING: Driver communication issue");
    }
}

void configureTMCDriver(TMC2209Stepper& driver, uint16_t current_mA, bool stealthchop) {
    // Begin communication
    driver.begin();
    
    // Set current (mA)
    driver.rms_current(current_mA);
    
    // Microstepping (256 interpolated from 16)
    driver.microsteps(16);
    driver.intpol(true);  // Interpolate to 256
    
    // Enable StealthChop or SpreadCycle
    driver.en_spreadCycle(!stealthchop);
    driver.pwm_autoscale(true);
    driver.pwm_autograd(true);
    
    // Set blank time and off-time for optimal operation
    driver.blank_time(24);
    driver.toff(5);
    
    // Enable driver
    driver.shaft(false);  // Direction
    driver.pdn_disable(true);  // Disable PDN pin (use UART instead)
    driver.mstep_reg_select(true);  // Use microstep register
    
    // Coolstep settings (optional - for higher currents)
    // driver.TCOOLTHRS(0xFFFFF);  // Enable coolstep at all speeds
    // driver.semin(5);
    // driver.semax(2);
}

void setMotorCurrent(char axis, uint16_t current_mA) {
    TMC2209Stepper* driver = nullptr;
    
    switch (axis) {
        case 'X': case 'x': driver = &tmc_x; break;
        case 'Y': case 'y': driver = &tmc_y; break;
        case 'Z': case 'z': driver = &tmc_z; break;
        case 'E': case 'e': driver = &tmc_e; break;
        default: return;
    }
    
    if (driver) {
        driver->rms_current(current_mA);
        Serial.print("Set ");
        Serial.print(axis);
        Serial.print(" current to ");
        Serial.print(current_mA);
        Serial.println("mA");
    }
}

void setStealthChop(char axis, bool enable) {
    TMC2209Stepper* driver = nullptr;
    
    switch (axis) {
        case 'X': case 'x': driver = &tmc_x; break;
        case 'Y': case 'y': driver = &tmc_y; break;
        case 'Z': case 'z': driver = &tmc_z; break;
        case 'E': case 'e': driver = &tmc_e; break;
        default: return;
    }
    
    if (driver) {
        driver->en_spreadCycle(!enable);
        Serial.print(axis);
        Serial.print(enable ? " StealthChop enabled" : " SpreadCycle enabled");
        Serial.println();
    }
}

bool checkDriverStatus() {
    bool allOK = true;
    
    // Check each driver can communicate
    if (!tmc_x.test_connection()) {
        Serial.println("ERROR: TMC X no response");
        allOK = false;
    }
    
    if (!tmc_y.test_connection()) {
        Serial.println("ERROR: TMC Y no response");
        allOK = false;
    }
    
    if (!tmc_z.test_connection()) {
        Serial.println("ERROR: TMC Z no response");
        allOK = false;
    }
    
    if (!tmc_e.test_connection()) {
        Serial.println("ERROR: TMC E no response");
        allOK = false;
    }
    
    return allOK;
}

uint8_t getDriverTempStatus(char axis) {
    TMC2209Stepper* driver = nullptr;
    
    switch (axis) {
        case 'X': case 'x': driver = &tmc_x; break;
        case 'Y': case 'y': driver = &tmc_y; break;
        case 'Z': case 'z': driver = &tmc_z; break;
        case 'E': case 'e': driver = &tmc_e; break;
        default: return 0;
    }
    
    if (driver) {
        if (driver->otpw()) return 1;      // Over-temp warning
        if (driver->ot()) return 2;        // Over-temp shutdown
    }
    
    return 0;  // OK
}

void enableStallDetection(char axis, uint8_t threshold) {
    TMC2209Stepper* driver = nullptr;
    
    switch (axis) {
        case 'X': case 'x': driver = &tmc_x; break;
        case 'Y': case 'y': driver = &tmc_y; break;
        case 'Z': case 'z': driver = &tmc_z; break;
        case 'E': case 'e': driver = &tmc_e; break;
        default: return;
    }
    
    if (driver) {
        driver->SGTHRS(threshold);
        driver->TCOOLTHRS(0xFFFFF);  // Enable at all speeds
        Serial.print("Stall detection enabled on ");
        Serial.print(axis);
        Serial.print(" with threshold ");
        Serial.println(threshold);
    }
}

bool isStalled(char axis) {
    TMC2209Stepper* driver = nullptr;
    
    switch (axis) {
        case 'X': case 'x': driver = &tmc_x; break;
        case 'Y': case 'y': driver = &tmc_y; break;
        case 'Z': case 'z': driver = &tmc_z; break;
        case 'E': case 'e': driver = &tmc_e; break;
        default: return false;
    }
    
    if (driver) {
        return driver->SG_RESULT() < driver->SGTHRS();
    }
    
    return false;
}

#endif // TMC_UART_ENABLED
