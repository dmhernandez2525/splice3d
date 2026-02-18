/**
 * Splice3D Multi-Printer Coordination For Print Farms (F10.3).
 *
 * Multi-printer job distribution, shared material pool management, farm-wide statistics.
 */

#ifndef PRINT_FARM_H
#define PRINT_FARM_H

#include <Arduino.h>

constexpr uint8_t kMaxPrinters = 8;
constexpr uint8_t kMaxFarmJobs = 32;
enum class PrinterState : uint8_t {
    OFFLINE = 0,
    IDLE = 1,
    PRINTING = 2,
    SPLICING = 3,
    ERROR = 4,
    MAINTENANCE = 5,
};

struct PrintFarmStats {
    uint32_t totalPrinters;
    uint16_t activePrinters;
    uint32_t totalFarmJobs;
    uint16_t completedFarmJobs;
    uint16_t avgJobMinutes;
    float farmUtilization;
};

void setupPrintFarm();
void updatePrintFarm();
PrintFarmStats getPrintFarmStats();
void serializePrintFarmStats();

#endif  // PRINT_FARM_H
