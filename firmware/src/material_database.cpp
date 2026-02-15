#include "material_database.h"
#include "config.h"
namespace {
struct DbState {
    MaterialProfile profiles[kMaxMaterials];
    uint8_t count;
};
DbState db;
void copyStr(char* dst, const char* src, uint8_t maxLen) {
    uint8_t i = 0;
    while (i < maxLen - 1 && src[i] != '\0') {
        dst[i] = src[i];
        i++;
    }
    dst[i] = '\0';
}
bool streq(const char* a, const char* b) {
    while (*a && *b) {
        if (*a != *b) return false;
        a++;
        b++;
    }
    return *a == *b;
}
void addDefault(const char* name, const char* brand, MaterialType type,
                uint16_t temp, uint16_t hold, float comp,
                uint16_t cool, float pull) {
    if (db.count >= kMaxMaterials) return;
    MaterialProfile& p = db.profiles[db.count];
    p = {};
    copyStr(p.name, name, kMaxNameLen);
    copyStr(p.brand, brand, kMaxBrandLen);
    p.type = type;
    p.spliceTemp = temp;
    p.holdTimeMs = hold;
    p.compressionMm = comp;
    p.coolTimeMs = cool;
    p.pullTestForceN = pull;
    p.active = true;
    db.count++;
}
}  // namespace
void setupMaterialDatabase() {
    db = {};
    loadDefaultMaterials();
    Serial.print(F("MATDB_INIT profiles="));
    Serial.println(db.count);
}
void updateMaterialDatabase() {
    // Database is passive; nothing to poll.
}
MaterialProfile getMaterialProfile(uint8_t index) {
    if (index >= db.count) return {};
    return db.profiles[index];
}
uint8_t getMaterialCount() { return db.count; }
uint8_t findMaterial(MaterialType type, const char* brand) {
    for (uint8_t i = 0; i < db.count; i++) {
        if (!db.profiles[i].active) continue;
        if (db.profiles[i].type == type && streq(db.profiles[i].brand, brand)) {
            return i;
        }
    }
    return 255;
}
uint8_t findMaterialByName(const char* name) {
    for (uint8_t i = 0; i < db.count; i++) {
        if (!db.profiles[i].active) continue;
        if (streq(db.profiles[i].name, name)) return i;
    }
    return 255;
}
uint8_t addMaterialProfile(const MaterialProfile& profile) {
    if (db.count >= kMaxMaterials) return 255;
    db.profiles[db.count] = profile;
    db.profiles[db.count].active = true;
    Serial.print(F("MATDB_ADD idx="));
    Serial.print(db.count);
    Serial.print(F(" name="));
    Serial.println(db.profiles[db.count].name);
    return db.count++;
}
bool updateMaterialProfile(uint8_t index, const MaterialProfile& profile) {
    if (index >= db.count) return false;
    db.profiles[index] = profile;
    db.profiles[index].active = true;
    Serial.print(F("MATDB_UPDATE idx="));
    Serial.println(index);
    return true;
}
bool removeMaterialProfile(uint8_t index) {
    if (index >= db.count) return false;
    if (!db.profiles[index].active) return false;
    db.profiles[index].active = false;
    Serial.print(F("MATDB_REMOVE idx="));
    Serial.println(index);
    return true;
}
bool serializeMaterialToSerial(uint8_t index) {
    if (index >= db.count) return false;
    const MaterialProfile& p = db.profiles[index];
    if (!p.active) return false;
    Serial.print(F("MAT idx="));
    Serial.print(index);
    Serial.print(F(" name="));
    Serial.print(p.name);
    Serial.print(F(" brand="));
    Serial.print(p.brand);
    Serial.print(F(" type="));
    Serial.print(static_cast<uint8_t>(p.type));
    Serial.print(F(" temp="));
    Serial.print(p.spliceTemp);
    Serial.print(F(" hold="));
    Serial.print(p.holdTimeMs);
    Serial.print(F(" comp="));
    Serial.print(p.compressionMm, 2);
    Serial.print(F(" cool="));
    Serial.print(p.coolTimeMs);
    Serial.print(F(" pull="));
    Serial.println(p.pullTestForceN, 1);
    return true;
}
void serializeAllMaterials() {
    Serial.print(F("MATDB_LIST count="));
    Serial.println(db.count);
    for (uint8_t i = 0; i < db.count; i++) {
        if (db.profiles[i].active) {
            serializeMaterialToSerial(i);
        }
    }
    Serial.println(F("MATDB_LIST_END"));
}
MaterialDbStats getMaterialDbStats() {
    MaterialDbStats stats = {};
    stats.totalProfiles = db.count;
    for (uint8_t i = 0; i < db.count; i++) {
        if (db.profiles[i].active) {
            stats.activeProfiles++;
            uint8_t t = static_cast<uint8_t>(db.profiles[i].type);
            if (t < static_cast<uint8_t>(MaterialType::MATERIAL_COUNT)) {
                stats.profilesByType[t]++;
            }
        }
    }
    return stats;
}
void loadDefaultMaterials() {
    // PLA defaults
    addDefault("PLA-Generic", "Generic", MaterialType::PLA,
               210, 3000, 2.0f, 5000, 5.0f);
    addDefault("PLA-Prusament", "Prusament", MaterialType::PLA,
               215, 3200, 2.1f, 5000, 5.5f);
    addDefault("PLA-Hatchbox", "Hatchbox", MaterialType::PLA,
               205, 2800, 1.9f, 4500, 4.8f);
    // PETG defaults
    addDefault("PETG-Generic", "Generic", MaterialType::PETG,
               235, 4000, 2.5f, 6000, 6.0f);
    addDefault("PETG-Prusament", "Prusament", MaterialType::PETG,
               240, 4200, 2.6f, 6500, 6.5f);
    // ABS defaults
    addDefault("ABS-Generic", "Generic", MaterialType::ABS,
               250, 4500, 3.0f, 8000, 7.0f);
    addDefault("ABS-Hatchbox", "Hatchbox", MaterialType::ABS,
               245, 4200, 2.8f, 7500, 6.8f);
    // TPU defaults
    addDefault("TPU-Generic", "Generic", MaterialType::TPU,
               220, 5000, 1.5f, 7000, 3.0f);
    addDefault("TPU-NinjaFlex", "NinjaTek", MaterialType::TPU,
               225, 5500, 1.2f, 7500, 2.8f);
}
