#include "print_farm.h"
#include "config.h"

namespace {

struct State {
    PrintFarmStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupPrintFarm() {
    st = {};
    st.initialized = true;
    Serial.println(F("PRINT_FARM_INIT"));
}

void updatePrintFarm() {
    if (!st.initialized) return;
}

PrintFarmStats getPrintFarmStats() {
    return st.stats;
}

void serializePrintFarmStats() {
    PrintFarmStats s = st.stats;
    Serial.print(F("PRINT_FARM_STATS"));
    Serial.print(F(" totalPrinters="));
    Serial.print(s.totalPrinters);
    Serial.print(F(" activePrinters="));
    Serial.print(s.activePrinters);
    Serial.print(F(" totalFarmJobs="));
    Serial.print(s.totalFarmJobs);
    Serial.print(F(" completedFarmJobs="));
    Serial.print(s.completedFarmJobs);
    Serial.print(F(" avgJobMinutes="));
    Serial.print(s.avgJobMinutes);
    Serial.print(F(" farmUtilization="));
    Serial.print(s.farmUtilization, 2);
    Serial.println();
}
