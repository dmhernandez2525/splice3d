/**
 * Splice3D Embedded Web Server For Splicer Monitoring (F9.2).
 *
 * Embedded web server with REST API, WebSocket real-time updates, and status pages.
 */

#ifndef WEB_DASHBOARD_H
#define WEB_DASHBOARD_H

#include <Arduino.h>

struct WebDashboardStats {
    uint32_t totalRequests;
    uint16_t activeConnections;
    uint16_t websocketClients;
    uint32_t uptimeMs;
    uint16_t bytesServed;
    uint32_t errorCount;
};

void setupWebDashboard();
void updateWebDashboard();
WebDashboardStats getWebDashboardStats();
void serializeWebDashboardStats();

#endif  // WEB_DASHBOARD_H
