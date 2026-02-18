/**
 * Splice3D Push Notification System For Splice Events (F9.4).
 *
 * Notification channel management with priorities, configurable event filters, delivery queue.
 */

#ifndef NOTIFICATION_MANAGER_H
#define NOTIFICATION_MANAGER_H

#include <Arduino.h>

constexpr uint8_t kMaxNotifications = 32;
constexpr uint8_t kMaxNotifChannels = 4;
enum class NotificationPriority : uint8_t {
    LOW = 0,
    MEDIUM = 1,
    HIGH = 2,
    CRITICAL = 3,
};

enum class NotificationEventType : uint8_t {
    SPLICE_COMPLETE = 0,
    SPLICE_FAILED = 1,
    TEMPERATURE_WARNING = 2,
    JOB_COMPLETE = 3,
    QUEUE_EMPTY = 4,
    ERROR = 5,
};

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
