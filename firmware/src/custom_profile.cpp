#include "custom_profile.h"
#include "config.h"
#include <EEPROM.h>
namespace {
struct ProfileEditorState {
    CustomProfileSlot slots[kMaxCustomProfiles];
    uint8_t corruptCount;
};
ProfileEditorState pe;
uint16_t slotEepromAddr(uint8_t slot) {
    return kEepromProfileBase
           + slot * (sizeof(CustomProfileHeader) + sizeof(MaterialProfile));
}
uint8_t checksumBytes(const uint8_t* data, uint16_t len) {
    uint8_t sum = 0;
    for (uint16_t i = 0; i < len; i++) {
        sum ^= data[i];
        sum = (sum << 1) | (sum >> 7);  // rotate left
    }
    return sum;
}
}  // namespace
uint8_t computeProfileChecksum(const MaterialProfile& profile) {
    return checksumBytes(
        reinterpret_cast<const uint8_t*>(&profile),
        sizeof(MaterialProfile)
    );
}
void setupCustomProfile() {
    pe = {};
    loadCustomProfilesFromEeprom();
    CustomProfileStats stats = getCustomProfileStats();
    Serial.print(F("CUSTPROF_INIT used="));
    Serial.print(stats.usedSlots);
    Serial.print(F("/"));
    Serial.println(stats.totalSlots);
}
void updateCustomProfile() {
    // Profile editor is passive; nothing to poll.
}
uint8_t createCustomProfile(const MaterialProfile& profile) {
    for (uint8_t i = 0; i < kMaxCustomProfiles; i++) {
        if (!pe.slots[i].occupied) {
            pe.slots[i].profile = profile;
            pe.slots[i].profile.active = true;
            pe.slots[i].header.magic = kProfileMagic;
            pe.slots[i].header.index = i;
            pe.slots[i].header.checksum = computeProfileChecksum(profile);
            pe.slots[i].occupied = true;
            Serial.print(F("CUSTPROF_CREATE slot="));
            Serial.print(i);
            Serial.print(F(" name="));
            Serial.println(profile.name);
            return i;
        }
    }
    Serial.println(F("CUSTPROF_FULL"));
    return 255;
}
bool modifyCustomProfile(uint8_t slot, const MaterialProfile& profile) {
    if (slot >= kMaxCustomProfiles) return false;
    if (!pe.slots[slot].occupied) return false;
    pe.slots[slot].profile = profile;
    pe.slots[slot].profile.active = true;
    pe.slots[slot].header.checksum = computeProfileChecksum(profile);
    Serial.print(F("CUSTPROF_MODIFY slot="));
    Serial.println(slot);
    return true;
}
bool deleteCustomProfile(uint8_t slot) {
    if (slot >= kMaxCustomProfiles) return false;
    if (!pe.slots[slot].occupied) return false;
    pe.slots[slot] = {};
    Serial.print(F("CUSTPROF_DELETE slot="));
    Serial.println(slot);
    return true;
}
CustomProfileSlot getCustomProfileSlot(uint8_t slot) {
    if (slot >= kMaxCustomProfiles) return {};
    return pe.slots[slot];
}
MaterialProfile getCustomProfile(uint8_t slot) {
    if (slot >= kMaxCustomProfiles) return {};
    if (!pe.slots[slot].occupied) return {};
    return pe.slots[slot].profile;
}
bool isSlotOccupied(uint8_t slot) {
    if (slot >= kMaxCustomProfiles) return false;
    return pe.slots[slot].occupied;
}
bool saveCustomProfilesToEeprom() {
    for (uint8_t i = 0; i < kMaxCustomProfiles; i++) {
        uint16_t addr = slotEepromAddr(i);
        if (pe.slots[i].occupied) {
            pe.slots[i].header.checksum =
                computeProfileChecksum(pe.slots[i].profile);
            EEPROM.put(addr, pe.slots[i].header);
            EEPROM.put(
                addr + sizeof(CustomProfileHeader),
                pe.slots[i].profile
            );
        } else {
            // Write zero magic to mark empty.
            CustomProfileHeader empty = {};
            EEPROM.put(addr, empty);
        }
    }
    Serial.println(F("CUSTPROF_SAVED"));
    return true;
}
bool loadCustomProfilesFromEeprom() {
    pe.corruptCount = 0;
    for (uint8_t i = 0; i < kMaxCustomProfiles; i++) {
        uint16_t addr = slotEepromAddr(i);
        CustomProfileHeader hdr = {};
        MaterialProfile prof = {};
        EEPROM.get(addr, hdr);
        if (hdr.magic != kProfileMagic) {
            pe.slots[i] = {};
            continue;
        }
        EEPROM.get(addr + sizeof(CustomProfileHeader), prof);
        uint8_t expected = computeProfileChecksum(prof);
        if (hdr.checksum != expected) {
            pe.slots[i] = {};
            pe.corruptCount++;
            Serial.print(F("CUSTPROF_CORRUPT slot="));
            Serial.println(i);
            continue;
        }
        pe.slots[i].header = hdr;
        pe.slots[i].profile = prof;
        pe.slots[i].occupied = true;
    }
    return true;
}
bool verifyEepromChecksum(uint8_t slot) {
    if (slot >= kMaxCustomProfiles) return false;
    if (!pe.slots[slot].occupied) return false;
    uint8_t expected = computeProfileChecksum(pe.slots[slot].profile);
    return pe.slots[slot].header.checksum == expected;
}
CustomProfileStats getCustomProfileStats() {
    CustomProfileStats stats = {};
    stats.totalSlots = kMaxCustomProfiles;
    stats.corruptSlots = pe.corruptCount;
    for (uint8_t i = 0; i < kMaxCustomProfiles; i++) {
        if (pe.slots[i].occupied) {
            stats.usedSlots++;
        } else {
            stats.freeSlots++;
        }
    }
    return stats;
}
void serializeCustomProfiles() {
    Serial.print(F("CUSTPROF_LIST slots="));
    Serial.println(kMaxCustomProfiles);
    for (uint8_t i = 0; i < kMaxCustomProfiles; i++) {
        if (!pe.slots[i].occupied) continue;
        const MaterialProfile& p = pe.slots[i].profile;
        Serial.print(F("CUSTPROF slot="));
        Serial.print(i);
        Serial.print(F(" name="));
        Serial.print(p.name);
        Serial.print(F(" type="));
        Serial.print(static_cast<uint8_t>(p.type));
        Serial.print(F(" temp="));
        Serial.print(p.spliceTemp);
        Serial.print(F(" chk="));
        Serial.println(pe.slots[i].header.checksum);
    }
    Serial.println(F("CUSTPROF_LIST_END"));
}
