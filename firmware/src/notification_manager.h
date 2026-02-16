/**
 * Splice3D Push Notification System For Splice Events (F9.4).
 *
 * Notification channel management with priorities, configurable event filters, delivery queue.
 */

#ifndef NOTIFICATION_MANAGER_H
#define NOTIFICATION_MANAGER_H

#include <Arduino.h>

struct NotificationManagerStats {
    uint32_t totalSent;
    uint32_t totalDelivered;
    uint32_t totalFailed;
    uint32_t pendingCount;
    uint32_t channelCount;
    uint32_t lastSentMs;
};

void setupNotificationManager();
void updateNotificationManager();
NotificationManagerStats getNotificationManagerStats();
void serializeNotificationManagerStats();

#endif  // NOTIFICATION_MANAGER_H
