#include "job_queue.h"
#include "config.h"
namespace {
struct QueueState {
    JobEntry jobs[kMaxQueuedJobs];
    uint8_t count;
    uint8_t currentIndex;
    uint16_t nextJobId;
    QueueStats stats;
    bool running;
};
QueueState jq;
int8_t findJob(uint16_t jobId) {
    for (uint8_t i = 0; i < jq.count; i++) {
        if (jq.jobs[i].jobId == jobId) return static_cast<int8_t>(i);
    }
    return -1;
}
void sortByPriority() {
    // Simple insertion sort by priority (higher = earlier).
    for (uint8_t i = 1; i < jq.count; i++) {
        JobEntry temp = jq.jobs[i];
        int8_t j = static_cast<int8_t>(i) - 1;
        while (j >= 0 && jq.jobs[j].priority < temp.priority) {
            jq.jobs[j + 1] = jq.jobs[j];
            j--;
        }
        jq.jobs[j + 1] = temp;
    }
}
void startJob(uint8_t index) {
    JobEntry& job = jq.jobs[index];
    job.status = JobStatus::RUNNING;
    job.startTimeMs = millis();
    jq.currentIndex = index;
    jq.running = true;
    Serial.print(F("JOB_START id="));
    Serial.print(job.jobId);
    Serial.print(F(" segs="));
    Serial.println(job.segmentCount);
}
void finishJob(JobStatus status) {
    if (!jq.running) return;
    JobEntry& job = jq.jobs[jq.currentIndex];
    job.status = status;
    job.elapsedMs = millis() - job.startTimeMs;
    job.progressPercent = (status == JobStatus::COMPLETE) ? 100.0f : job.progressPercent;
    jq.running = false;
    if (status == JobStatus::COMPLETE) {
        jq.stats.totalCompleted++;
        const float n = static_cast<float>(jq.stats.totalCompleted);
        jq.stats.avgJobTimeMs =
            ((n - 1.0f) * jq.stats.avgJobTimeMs +
             static_cast<float>(job.elapsedMs)) / n;
    } else if (status == JobStatus::FAILED) {
        jq.stats.totalFailed++;
    } else if (status == JobStatus::CANCELLED) {
        jq.stats.totalCancelled++;
    }
    Serial.print(F("JOB_END id="));
    Serial.print(job.jobId);
    Serial.print(F(" status="));
    Serial.println(static_cast<uint8_t>(status));
}
}  // namespace
void setupJobQueue() {
    jq = {};
    jq.nextJobId = 1;
}
void updateJobQueue() {
    if (!jq.running) return;
    JobEntry& job = jq.jobs[jq.currentIndex];
    if (job.status != JobStatus::RUNNING) return;
    job.elapsedMs = millis() - job.startTimeMs;
    if (job.segmentCount > 0) {
        job.progressPercent = static_cast<float>(job.currentSegment)
            / static_cast<float>(job.segmentCount) * 100.0f;
    }
}
int16_t enqueueJob(uint16_t segmentCount, uint8_t materialIndex, uint8_t priority) {
    if (jq.count >= kMaxQueuedJobs) return -1;
    JobEntry& job = jq.jobs[jq.count];
    job = {};
    job.jobId = jq.nextJobId++;
    job.segmentCount = segmentCount;
    job.materialIndex = materialIndex;
    job.priority = priority;
    job.status = JobStatus::PENDING;
    jq.count++;
    jq.stats.totalQueued++;
    sortByPriority();
    Serial.print(F("JOB_QUEUED id="));
    Serial.print(job.jobId);
    Serial.print(F(" pri="));
    Serial.println(priority);
    // Auto-start if nothing running and this is first pending job.
    if (!jq.running) {
        for (uint8_t i = 0; i < jq.count; i++) {
            if (jq.jobs[i].status == JobStatus::PENDING) {
                startJob(i);
                break;
            }
        }
    }
    return job.jobId;
}
bool cancelJob(uint16_t jobId) {
    const int8_t idx = findJob(jobId);
    if (idx < 0) return false;
    JobEntry& job = jq.jobs[idx];
    if (job.status == JobStatus::COMPLETE || job.status == JobStatus::CANCELLED) return false;
    if (job.status == JobStatus::RUNNING) {
        finishJob(JobStatus::CANCELLED);
    } else {
        job.status = JobStatus::CANCELLED;
        jq.stats.totalCancelled++;
    }
    return true;
}
bool pauseCurrentJob() {
    if (!jq.running) return false;
    JobEntry& job = jq.jobs[jq.currentIndex];
    if (job.status != JobStatus::RUNNING) return false;
    job.status = JobStatus::PAUSED;
    Serial.print(F("JOB_PAUSED id="));
    Serial.println(job.jobId);
    return true;
}
bool resumeCurrentJob() {
    if (!jq.running) return false;
    JobEntry& job = jq.jobs[jq.currentIndex];
    if (job.status != JobStatus::PAUSED) return false;
    job.status = JobStatus::RUNNING;
    Serial.print(F("JOB_RESUMED id="));
    Serial.println(job.jobId);
    return true;
}
void clearQueue() {
    if (jq.running) finishJob(JobStatus::CANCELLED);
    jq.count = 0;
    jq.running = false;
    Serial.println(F("JOB_QUEUE CLEARED"));
}
uint8_t getQueueLength() { return jq.count; }
JobEntry getJobEntry(uint8_t queueIndex) {
    if (queueIndex >= jq.count) return {};
    return jq.jobs[queueIndex];
}
JobEntry getCurrentJob() {
    if (!jq.running) return {};
    return jq.jobs[jq.currentIndex];
}
bool isQueueEmpty() { return jq.count == 0; }
bool isJobRunning() { return jq.running; }
QueueStats getQueueStats() { return jq.stats; }
void advanceQueue() {
    if (jq.running) {
        finishJob(JobStatus::COMPLETE);
    }
    // Find next pending job.
    for (uint8_t i = 0; i < jq.count; i++) {
        if (jq.jobs[i].status == JobStatus::PENDING) {
            startJob(i);
            return;
        }
    }
    Serial.println(F("JOB_QUEUE EMPTY"));
}
