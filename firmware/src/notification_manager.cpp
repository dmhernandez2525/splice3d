#include "notification_manager.h"
#include "config.h"

namespace {

struct State {
    NotificationManagerStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupNotificationManager() {
    st = {};
    st.initialized = true;
    Serial.println(F("NOTIFICATION_MANAGER_INIT"));
}

void updateNotificationManager() {
    if (!st.initialized) return;
}

NotificationManagerStats getNotificationManagerStats() {
    return st.stats;
}

void serializeNotificationManagerStats() {
    NotificationManagerStats s = st.stats;
    Serial.print(F("NOTIFICATION_MANAGER_STATS"));
    Serial.print(F(" totalSent="));
    Serial.print(s.totalSent);
    Serial.print(F(" totalDelivered="));
    Serial.print(s.totalDelivered);
    Serial.print(F(" totalFailed="));
    Serial.print(s.totalFailed);
    Serial.print(F(" pendingCount="));
    Serial.print(s.pendingCount);
    Serial.print(F(" channelCount="));
    Serial.print(s.channelCount);
    Serial.print(F(" lastSentMs="));
    Serial.print(s.lastSentMs);
    Serial.println();
}
