#include "web_dashboard.h"
#include "config.h"

namespace {

struct State {
    WebDashboardStats stats;
    bool initialized;
};

State st;

}  // namespace

void setupWebDashboard() {
    st = {};
    st.initialized = true;
    Serial.println(F("WEB_DASHBOARD_INIT"));
}

void updateWebDashboard() {
    if (!st.initialized) return;
}

WebDashboardStats getWebDashboardStats() {
    return st.stats;
}

void serializeWebDashboardStats() {
    WebDashboardStats s = st.stats;
    Serial.print(F("WEB_DASHBOARD_STATS"));
    Serial.print(F(" totalRequests="));
    Serial.print(s.totalRequests);
    Serial.print(F(" activeConnections="));
    Serial.print(s.activeConnections);
    Serial.print(F(" websocketClients="));
    Serial.print(s.websocketClients);
    Serial.print(F(" uptimeMs="));
    Serial.print(s.uptimeMs);
    Serial.print(F(" bytesServed="));
    Serial.print(s.bytesServed);
    Serial.print(F(" errorCount="));
    Serial.print(s.errorCount);
    Serial.println();
}
