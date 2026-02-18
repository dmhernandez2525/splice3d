/**
 * Splice3D Custom Profile Editor (F5.3).
 *
 * Runtime API for creating, modifying, and deleting custom material
 * profiles. Stores profiles in EEPROM with checksum validation for
 * persistence across power cycles.
 */

#ifndef CUSTOM_PROFILE_H
#define CUSTOM_PROFILE_H

#include <Arduino.h>
#include "material_database.h"

constexpr uint8_t kMaxCustomProfiles = 8;
constexpr uint16_t kEepromProfileBase = 128;
constexpr uint8_t kProfileMagic = 0xA5;

struct CustomProfileHeader {
    uint8_t magic;
    uint8_t index;
    uint8_t checksum;
    uint8_t reserved;
};

struct CustomProfileSlot {
    CustomProfileHeader header;
    MaterialProfile profile;
    bool occupied;
};

struct CustomProfileStats {
    uint8_t totalSlots;
    uint8_t usedSlots;
    uint8_t freeSlots;
    uint8_t corruptSlots;
};

void setupCustomProfile();
void updateCustomProfile();

// Create a new custom profile. Returns slot index or 255 on failure.
uint8_t createCustomProfile(const MaterialProfile& profile);

// Modify an existing custom profile by slot index.
bool modifyCustomProfile(uint8_t slot, const MaterialProfile& profile);

// Delete a custom profile by slot index.
bool deleteCustomProfile(uint8_t slot);

// Read a custom profile by slot index.
CustomProfileSlot getCustomProfileSlot(uint8_t slot);
MaterialProfile getCustomProfile(uint8_t slot);
bool isSlotOccupied(uint8_t slot);

// EEPROM persistence.
bool saveCustomProfilesToEeprom();
bool loadCustomProfilesFromEeprom();
bool verifyEepromChecksum(uint8_t slot);

// Compute checksum for a profile.
uint8_t computeProfileChecksum(const MaterialProfile& profile);

// Statistics.
CustomProfileStats getCustomProfileStats();

// Serialize to serial.
void serializeCustomProfiles();

#endif  // CUSTOM_PROFILE_H
