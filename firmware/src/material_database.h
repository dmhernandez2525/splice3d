/**
 * Splice3D Material Database (F5.1).
 *
 * Expanded material profile storage with brand-specific settings
 * for PLA, PETG, ABS, and TPU. Provides lookup, add/update, and
 * serialization APIs for material profiles.
 */

#ifndef MATERIAL_DATABASE_H
#define MATERIAL_DATABASE_H

#include <Arduino.h>

constexpr uint8_t kMaxMaterials = 24;
constexpr uint8_t kMaxNameLen = 16;
constexpr uint8_t kMaxBrandLen = 12;

enum class MaterialType : uint8_t {
    PLA = 0,
    PETG,
    ABS,
    TPU,
    MATERIAL_COUNT,
};

struct MaterialProfile {
    char name[kMaxNameLen];
    char brand[kMaxBrandLen];
    MaterialType type;
    uint16_t spliceTemp;       // Celsius
    uint16_t holdTimeMs;       // Splice hold time
    float compressionMm;       // Push distance during splice
    uint16_t coolTimeMs;       // Cooling period
    float pullTestForceN;      // Pull test threshold in Newtons
    bool active;               // Slot in use
};

struct MaterialDbStats {
    uint8_t totalProfiles;
    uint8_t activeProfiles;
    uint8_t profilesByType[static_cast<uint8_t>(MaterialType::MATERIAL_COUNT)];
};

void setupMaterialDatabase();
void updateMaterialDatabase();

// Lookup by index.
MaterialProfile getMaterialProfile(uint8_t index);
uint8_t getMaterialCount();

// Lookup by type and brand. Returns index or 255 on miss.
uint8_t findMaterial(MaterialType type, const char* brand);

// Lookup by name. Returns index or 255 on miss.
uint8_t findMaterialByName(const char* name);

// Add or update a profile. Returns index or 255 on failure.
uint8_t addMaterialProfile(const MaterialProfile& profile);
bool updateMaterialProfile(uint8_t index, const MaterialProfile& profile);
bool removeMaterialProfile(uint8_t index);

// Serialization helpers.
bool serializeMaterialToSerial(uint8_t index);
void serializeAllMaterials();

// Database stats.
MaterialDbStats getMaterialDbStats();

// Populate built-in defaults for PLA/PETG/ABS/TPU.
void loadDefaultMaterials();

#endif  // MATERIAL_DATABASE_H
