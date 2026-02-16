/**
 * Splice3D Multi-Printer Coordination For Print Farms (F10.3).
 *
 * Multi-printer job distribution, shared material pool management, farm-wide statistics.
 */

#ifndef PRINT_FARM_H
#define PRINT_FARM_H

#include <Arduino.h>

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
